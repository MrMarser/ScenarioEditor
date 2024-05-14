# -*- coding: utf-8 -*-
import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QGroupBox, QVBoxLayout, QLabel, QPushButton, QDockWidget, QTreeWidget, QTreeWidgetItem, QFileDialog, QToolBar, QMenu, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QMessageBox
from PyQt6.QtGui import QAction, QIcon, QWheelEvent, QPainter, QPen, QBrush
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):

    


    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scenario Editor")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()
        self.createCanvas()
        self.barMenu()
        self.TollBar()
        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderHidden(True)
        self.setupDockWidget()
        self.connectSignals()
        self.inspectorDockWidget()

    def barMenu(self):
        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")
        menu.setStyleSheet(Path("main/menuBar.css").read_text())

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

    def TollBar(self):
        toolbar = QToolBar("Tool bar")
        self.addToolBar(toolbar)
        toolbar.setStyleSheet("color: white; font-size: 15px")

        selectBackground = QAction("Background", self)
        toolbar.addAction(selectBackground) 

        addSprite = QAction("add Sprite", self)
        toolbar.addAction(addSprite)

        newFrame = QAction("new Frame", self)
        toolbar.addAction(newFrame)

        playAnimation = QAction("play Animation", self)
        toolbar.addAction(playAnimation)

        selectBackground.triggered.connect(self.showBackgroundMenu)
        # More TODO

        self.toolbar = toolbar

    def showBackgroundMenu(self):
        menu = QMenu()
        imageActions = []
        imageFiles = self.images()
        backgroundFolder = "backgrounds/"
        for imageFile in imageFiles:
            action = QAction(QIcon(backgroundFolder + imageFile), imageFile, self)
            imageActions.append(action)
            menu.addAction(action)

        action = self.sender()

        if self.toolbar:
            pos = self.toolbar.actionGeometry(action).bottomLeft()
            pos = self.toolbar.mapToGlobal(pos)
            menu.exec(pos)

    def images(self):
        photos = []
        file_dir = "backgrounds/"
        for file_name in os.listdir(file_dir):
            file_path = os.path.join(file_dir, file_name)
            if os.path.isfile(file_path) and file_name.lower().endswith(".png"):
                photos.append(file_name)
        return photos

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
            background-color: rgb(30, 40, 50);
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
        for key, _ in data.items():
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

            if data[key]["background"]["animation"]:
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

            if data[key]["sprites"]["count"] > 0:
                spriteArr = []
                for v in range(data[key]["sprites"]["count"]):
                    spriteArr.append(QTreeWidgetItem(["sptrite " + str(v+1)]))
                    sprites.addChild(spriteArr[v])

                    spriteArr[v].addChild(QTreeWidgetItem(["name"]))
                    spriteArr[v].addChild(QTreeWidgetItem(["pose"]))
                    spriteArr[v].addChild(QTreeWidgetItem(["position"]))
                    spriteArr[v].addChild(QTreeWidgetItem(["scale"]))
                    

                    if data[key]["sprites"][str(v+1)]["animation"] == True:
                        animation_item = QTreeWidgetItem(["animation"])
                        spriteArr[v].addChild(animation_item)
                        animation_item.addChild(QTreeWidgetItem(["time"]))
                        animation_item.addChild(QTreeWidgetItem(["position"]))
                        animation_item.addChild(QTreeWidgetItem(["scale"]))
                    else:
                        spriteArr[v].addChild(QTreeWidgetItem(["animation"]))


            

            
                    
            #music #TODO
    def inspectorDockWidget(self):
        self.inspectorDock = QDockWidget("Element inspector", self)
        self.inspectorGroup = QGroupBox("")
        self.inspectorDock.setWidget(self.inspectorGroup)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.inspectorDock)
        self.inspectorGroup.setLayout(QVBoxLayout())  # Инициализация макета для содержимого
        self.inspectorGroup.setStyleSheet("""
            QGroupBox {
                background-color: rgb(50, 70, 90); 
                color: white; 
                font-size: 14px; 
            }
        """)
        self.inspectorDock.setStyleSheet("""
            background-color: rgb(30, 40, 50);
            color: white;
        """)

    def inspectorLoad(self, path):
        layout = self.inspectorGroup.layout()
        key = path[0]
        data = self.content
        print(data)
        

            

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.setStyleSheet(Path("main/style.css").read_text())

sys.exit(app.exec())
