# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QScrollArea, QDialog, QWidget, QGridLayout, QHBoxLayout, QGroupBox, QVBoxLayout, QFormLayout, QLabel, QPushButton, QDockWidget, QTreeWidget, QTreeWidgetItem, QFileDialog, QToolBar, QMenu, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QMessageBox
from PyQt6.QtGui import QAction, QIcon, QWheelEvent, QPainter, QPen, QBrush, QPixmap
from PyQt6.QtCore import Qt

BACKGROUND_FOLDER = "backgrounds/"

class BackgroundWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.initUi()

    def initUi(self):
        self.setWindowTitle("Background")
        self.resize(800, 800)

        mainLayout = QVBoxLayout(self)
        self.imageLayout = QGridLayout()

        scrollArea = QScrollArea(self)
        scrollAreaWidget = QWidget()
        scrollAreaWidget.setLayout(self.imageLayout)
        scrollArea.setWidget(scrollAreaWidget)
        scrollArea.setWidgetResizable(True)

        mainLayout.addWidget(scrollArea)
        self.setLayout(mainLayout)

        photos = self.images()
        self.populateGrid(self.imageLayout, photos)

        buttonLayout = QHBoxLayout()
        buttonContainer = QWidget()
        buttonContainer.setLayout(buttonLayout)
        mainLayout.addWidget(buttonContainer)

        backButton = QPushButton("Back", self)
        openBackgroundFolder = QPushButton("Open background folder", self)
        refreshButton = QPushButton("Refresh", self)

        buttonLayout.addWidget(backButton)
        buttonLayout.addWidget(openBackgroundFolder)
        buttonLayout.addWidget(refreshButton)

        backButton.clicked.connect(self.onBackButton)
        openBackgroundFolder.clicked.connect(self.onOpenBackgroundFolder)
        refreshButton.clicked.connect(self.onRefreshButton)

    def onBackButton(self):
        self.accept()

    def onOpenBackgroundFolder(self):
        if os.path.exists(BACKGROUND_FOLDER):
            if os.name == 'nt':
                os.startfile(BACKGROUND_FOLDER)
            elif os.name == 'posix':
                subprocess.call(['open', BACKGROUND_FOLDER] if sys.platform == 'darwin' else ['xdg-open', BACKGROUND_FOLDER])

    def onRefreshButton(self):
        self.photos = self.images()
        self.populateGrid(self.imageLayout, self.photos)

    def images(self):
        photos = []
        for file_name in os.listdir(BACKGROUND_FOLDER):
            file_path = os.path.join(BACKGROUND_FOLDER, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(".png"):
                photos.append((file_name, file_path))
        return photos

    def clearLayout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                self.clearLayout(item.layout())

    def populateGrid(self, layout, photos):
        row, col, max_cols = 0, 0, 2
        self.clearLayout(layout)
        for file_name, file_path in photos:
            pixmap = QPixmap(file_path)
            imageLabel = QLabel()
            imageLabel.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            imageLabel.setScaledContents(False)
            imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            imageLabel.mousePressEvent = self.onImageClicked(file_path)

            textLabel = QLabel(file_name)
            textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

            vbox = QVBoxLayout()
            vbox.addWidget(imageLabel)
            vbox.addWidget(textLabel)

            containerWidget = QWidget()
            containerWidget.setLayout(vbox)

            layout.addWidget(containerWidget, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1

    def onImageClicked(self, photo):
        def handler(event):
            print(f"Image clicked: {photo}")
            self.accept()
        return handler

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scenario Editor")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        self.createCanvas()
        self.barMenu()
        self.toolbar()
        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderHidden(True)
        self.setupDockWidget()
        self.connectSignals()
        self.inspectorDockWidget()

    def barMenu(self):
        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")
        menu.setStyleSheet("""
            QMenuBar {
                font-size: 15px;
                background-color: rgb(50, 70, 90);
                color: white;
            }
            QMenuBar::item:selected {
                background-color: black;
                color: white;
            }
            QMenu {
                font-size: 15px;
                background-color: rgb(50, 70, 90);
            }
            QMenu::item {
                background-color: transparent;
                color: white;
            }
            QMenu::item:selected {
                background-color: black;
                color: white;
            }
        """)

        openAction = QAction("&Open", self)
        fileMenu.addAction(openAction)
        saveAction = QAction("&Save", self)
        fileMenu.addAction(saveAction)
        saveAsAction = QAction("&Save As...", self)
        fileMenu.addAction(saveAsAction)
        fileMenu.addSeparator()
        exitAction = QAction("&Exit", self)
        fileMenu.addAction(exitAction)

        openAction.triggered.connect(self.openFile)
        exitAction.triggered.connect(self.close)

        openAction.setShortcut("Ctrl+O")
        saveAction.setShortcut("Ctrl+S")
        saveAsAction.setShortcut("Ctrl+Shift+S")
        exitAction.setShortcut("Ctrl+Q")

    def openFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open file", "", "JSON files (*.json)")
        if fileName:
            try:
                with open(fileName, "r", encoding="utf-8") as file:
                    self.content = json.load(file)
                    self.dockTreeWidget(self.content)
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Failed to load file: {e}")

    def toolbar(self):
        toolbar = QToolBar("Tool bar")
        self.addToolBar(toolbar)
        toolbar.setStyleSheet("""
            QToolBar {
                color: white;
            }
            QToolButton {
                font-size: 15px;
                color: white;
                border: none;
                padding: 5px 10px;
            }
            QToolButton:hover {
                background: white;
                color: black;
            }
        """)

        selectBackground = QAction("Background", self)
        toolbar.addAction(selectBackground)

        addSprite = QAction("Add Sprite", self)
        toolbar.addAction(addSprite)

        newFrame = QAction("New Frame", self)
        toolbar.addAction(newFrame)

        playAnimation = QAction("Play Animation", self)
        toolbar.addAction(playAnimation)

        selectBackground.triggered.connect(self.openBackgroundWindow)
        # More TODO

        self.toolbar = toolbar

    def openBackgroundWindow(self):
        self.backgroundwindow = BackgroundWindow()
        self.backgroundwindow.exec()

    def createCanvas(self):
        scene = QGraphicsScene()
        view = QGraphicsView(scene)
        view.setSceneRect(0, 0, 1600, 900)
        view.setRenderHint(QPainter.RenderHint.Antialiasing)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        view.wheelEvent = self.zoom
        rect_item = scene.addRect(0, 0, 1600, 900)
        pen = QPen(Qt.GlobalColor.black)
        rect_item.setPen(pen)
        view.setStyleSheet("background-color: rgb(50, 70, 90)")
        insideRect = QGraphicsRectItem(view.sceneRect())
        insideRect.setBrush(QBrush(Qt.GlobalColor.white))
        scene.addItem(insideRect)
        self.setCentralWidget(view)

    def zoom(self, event: QWheelEvent):
        view = self.centralWidget()
        factor = 1.1
        if event.angleDelta().y() > 0:
            view.scale(factor, factor)
        else:
            view.scale(1/factor, 1/factor)

    def setupDockWidget(self):
        dockWidget = QDockWidget("Scene Elements", self)
        dockWidget.setWidget(self.treeWidget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dockWidget)
        self.treeWidget.header().setStyleSheet("""
            QHeaderView::section {
                background-color: rgb(50, 70, 90); 
                color: white; 
                font-size: 14px;
            }
        """)
        dockWidget.setStyleSheet("""
            background-color: rgb(50, 70, 90);
            color: white;
        """)

    def connectSignals(self):
        self.treeWidget.itemClicked.connect(self.onItemClicked)

    def onItemClicked(self, item):
        self.path = []
        while item is not None:
            self.path.append(item.text(0))
            item = item.parent()
        self.path.reverse()
        self.inspectorLoad(self.path)

    def dockTreeWidget(self, data):
        self.treeWidget.clear()
        self.loadTreeItems(data)

    def loadTreeItems(self, data):
        for key, value in data.items():
            root = QTreeWidgetItem(self.treeWidget, [str(key)])
            self.treeWidget.addTopLevelItem(root)
            background = QTreeWidgetItem(["background"])
            text = QTreeWidgetItem(["text"])
            ui = QTreeWidgetItem(["ui"])
            sprites = QTreeWidgetItem(["sprites"])
            music = QTreeWidgetItem(["music"])

            root.addChild(background)
            root.addChild(text)
            root.addChild(ui)
            root.addChild(sprites)
            root.addChild(music)

            backgroundName = QTreeWidgetItem(["name"])
            backgroundPosition = QTreeWidgetItem(["position"])
            backgroundScale = QTreeWidgetItem(["scale"])
            backgroundAnimation = QTreeWidgetItem(["animation"])

            background.addChild(backgroundName)
            background.addChild(backgroundPosition)
            background.addChild(backgroundScale)
            background.addChild(backgroundAnimation)

            animationTime = QTreeWidgetItem(["time"])
            animationPosition = QTreeWidgetItem(["position"])
            animationScale = QTreeWidgetItem(["scale"])

            if value["background"].get("animation"):
                backgroundAnimation.addChild(animationTime)
                backgroundAnimation.addChild(animationPosition)
                backgroundAnimation.addChild(animationScale)

            textCharaName = QTreeWidgetItem(["Character name"])
            textText = QTreeWidgetItem(["text"])

            text.addChild(textCharaName)
            text.addChild(textText)

            uiTime = QTreeWidgetItem(["times of day"])
            uiChapter = QTreeWidgetItem(["chapter"])
            uiCharaEmotion = QTreeWidgetItem(["chara emotion"])

            ui.addChild(uiTime)
            ui.addChild(uiChapter)
            ui.addChild(uiCharaEmotion)

            if value["sprites"]["count"] > 0:
                spriteArr = []
                for v in range(value["sprites"]["count"]):
                    spriteArr.append(QTreeWidgetItem(["sprite " + str(v + 1)]))
                    sprites.addChild(spriteArr[v])

                    spriteArr[v].addChild(QTreeWidgetItem(["name"]))
                    spriteArr[v].addChild(QTreeWidgetItem(["pose"]))
                    spriteArr[v].addChild(QTreeWidgetItem(["position"]))
                    spriteArr[v].addChild(QTreeWidgetItem(["scale"]))

                    if value["sprites"][str(v + 1)]["animation"] == True:
                        animation_item = QTreeWidgetItem(["animation"])
                        spriteArr[v].addChild(animation_item)
                        animation_item.addChild(QTreeWidgetItem(["time"]))
                        animation_item.addChild(QTreeWidgetItem(["position"]))
                        animation_item.addChild(QTreeWidgetItem(["scale"]))
                    else:
                        spriteArr[v].addChild(QTreeWidgetItem(["animation"]))

    def inspectorDockWidget(self):
        self.inspectorDock = QDockWidget("Element inspector", self)
        self.inspectorGroup = QGroupBox("")
        self.inspectorDock.setWidget(self.inspectorGroup)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspectorDock)
        self.inspectorGroup.setLayout(QVBoxLayout())
        self.inspectorGroup.setStyleSheet("""
            QGroupBox {
                background-color: rgb(50, 70, 90);
                color: white;
                font-size: 14px;
            }
        """)
        self.inspectorDock.setStyleSheet("""
            background-color: rgb(50, 70, 90);
            color: white;
        """)

    def inspectorLoad(self, path):
        layout = self.inspectorGroup.layout()
        key = path[0]
        data = self.content
        formLayout = QFormLayout()
        # Continue implementing form layout loading logic

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())