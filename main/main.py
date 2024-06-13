# -*- coding: utf-8 -*-
import sys
import os
import subprocess
import json
from functools import partial
from PyQt6.QtWidgets import (QApplication, QMainWindow, QScrollArea, QDialog, QWidget, 
                             QGridLayout, QHBoxLayout, QGroupBox, QVBoxLayout, QFormLayout, 
                             QLabel, QPushButton, QDockWidget, QTreeWidget, QTreeWidgetItem, 
                             QFileDialog, QToolBar, QGraphicsView, QGraphicsScene, 
                             QGraphicsRectItem, QMessageBox, QSpinBox, QCheckBox,
                             QComboBox, QTextEdit, QListWidget, QDoubleSpinBox, QFrame,
                             QLineEdit, QListWidgetItem, QBoxLayout, )
from PyQt6.QtGui import QAction, QIcon, QWheelEvent, QPainter, QPen, QBrush, QPixmap
from PyQt6.QtCore import Qt, pyqtSignal

BACKGROUND_FOLDER = "backgrounds/"
SPRITES_FOLDER =  "sprites/basic"
MAIN_HERO_EMOTION_FOLDER = "sprites/makishiro"

BUFFER_DATA = {}

class SelectMainHeroEmotion(QDialog):
    emotionSelected = pyqtSignal(str)  # Сигнал, который передает путь к выбранному изображению

    def __init__(self):
        super().__init__()
        self.initUi()
    
    def initUi(self):
        self.setWindowTitle("Emotion")
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
        openBackgroundFolder = QPushButton("Open folder", self)
        refreshButton = QPushButton("Refresh", self)

        buttonLayout.addWidget(backButton)
        buttonLayout.addWidget(openBackgroundFolder)
        buttonLayout.addWidget(refreshButton)

        backButton.clicked.connect(self.onBackButton)
        openBackgroundFolder.clicked.connect(self.onOpenFolder)
        refreshButton.clicked.connect(self.onRefreshButton)

    def onBackButton(self):
        self.accept()

    def onOpenFolder(self):
        folder_path = os.path.abspath(MAIN_HERO_EMOTION_FOLDER)
        print(f"Current working directory: {os.getcwd()}")
        print(f"Checking if folder exists: {folder_path}")

        if os.path.exists(folder_path):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':
                    if sys.platform == 'darwin':  # macOS
                        subprocess.call(['open', folder_path])
                    else:  # Linux
                        subprocess.call(['xdg-open', folder_path])
            except Exception as e:
                print(f"Failed to open folder: {e}")
        else:
            print(f"Folder does not exist: {folder_path}")

    def onRefreshButton(self):
        self.photos = self.images()
        self.populateGrid(self.imageLayout, self.photos)

    def images(self):
        photos = []
        for file_name in os.listdir(MAIN_HERO_EMOTION_FOLDER):
            file_path = os.path.join(MAIN_HERO_EMOTION_FOLDER, file_name)
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
        self.clearLayout(layout)
        row, col, max_cols = 0, 0, 3 
        for file_name, file_path in photos:
            containerWidget = QWidget()
            formLayout = QFormLayout(containerWidget)
            formLayout.setVerticalSpacing(5)

            pixmap = QPixmap(file_path)
            imageLabel = QLabel()
            imageLabel.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            imageLabel.mousePressEvent = self.onImageClicked(file_path)

            textLabel = QLabel(file_name)
            textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

            formLayout.addRow(imageLabel)
            formLayout.addRow(textLabel)
            layout.addWidget(containerWidget, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1


    def onImageClicked(self, photo):
        def handler(event):
            self.emotionSelected.emit(photo)
            self.accept()
        return handler

class SpriteWindow(QDialog):
    sprite = pyqtSignal(str)

    def __init__(self, key, index):
        self.key = key
        self.index = index
        super().__init__()
        self.initUi()
    
    def initUi(self):
        self.setWindowTitle("Sprite")
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
        openSpritesFolder = QPushButton("Open sprites folder", self)
        refreshButton = QPushButton("Refresh", self)

        buttonLayout.addWidget(backButton)
        buttonLayout.addWidget(openSpritesFolder)
        buttonLayout.addWidget(refreshButton)

        backButton.clicked.connect(self.onBackButton)
        openSpritesFolder.clicked.connect(self.onOpenSpritesFolder)
        refreshButton.clicked.connect(self.onRefreshButton)

    def onBackButton(self):
        global SPRITES_FOLDER
        if SPRITES_FOLDER == "sprites/basic":
            self.accept()
        else:
            SPRITES_FOLDER = "sprites/basic"
            self.photos = self.images()
            self.populateGrid(self.imageLayout, self.photos)

    def onOpenSpritesFolder(self):
        folder_path = os.path.abspath(SPRITES_FOLDER)
        print(f"Current working directory: {os.getcwd()}")
        print(f"Checking if folder exists: {folder_path}")

        if os.path.exists(folder_path):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':
                    if sys.platform == 'darwin':  # macOS
                        subprocess.call(['open', folder_path])
                    else:  # Linux
                        subprocess.call(['xdg-open', folder_path])
            except Exception as e:
                print(f"Failed to open folder: {e}")
        else:
            print(f"Folder does not exist: {folder_path}")

    def onRefreshButton(self):
        self.photos = self.images()
        self.populateGrid(self.imageLayout, self.photos)

    def images(self):
        photos = []
        for file_name in os.listdir(SPRITES_FOLDER):
            file_path = os.path.join(SPRITES_FOLDER, file_name)
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
        self.clearLayout(layout)
        row, col, max_cols = 0, 0, 3  
        for file_name, file_path in photos:
            containerWidget = QWidget()
            formLayout = QFormLayout(containerWidget)
            formLayout.setVerticalSpacing(5)

            pixmap = QPixmap(file_path)
            imageLabel = QLabel()
            imageLabel.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            imageLabel.mousePressEvent = self.onImageClicked(file_path)

            textLabel = QLabel(file_name)
            textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

            formLayout.addRow(imageLabel)
            formLayout.addRow(textLabel)
            layout.addWidget(containerWidget, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1



    def onImageClicked(self, file_path):
        def handler(event):
            global SPRITES_FOLDER
            BUFFER_SPRITES_FOLDER = SPRITES_FOLDER
            new_folder = os.path.join(SPRITES_FOLDER[:-5], os.path.basename(file_path)[:-4])
            
            if os.path.exists(new_folder):
                SPRITES_FOLDER = new_folder
                self.photos = self.images()
                self.populateGrid(self.imageLayout, self.photos)
            else:
                if self.index == None:
                    count = BUFFER_DATA[self.key]["sprites"]["count"]
                    BUFFER_DATA[self.key]["sprites"]["count"] = count+1
                    BUFFER_DATA[self.key]["sprites"][str(count)] = {"objectName": "",
                "name": file_path,
                "position":{
                    "x": 0,
                    "y": 0
                },
                "scale":{
                    "x": 1,
                    "y": 1
                },
                "animation": False}
                else:
                    BUFFER_DATA[self.key]["sprites"][self.index]["name"] = file_path
                SPRITES_FOLDER = BUFFER_SPRITES_FOLDER
                self.accept()
        return handler

class BackgroundWindow(QDialog):
    def __init__(self, key):
        super().__init__()
        self.key = key
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
        folder_path = os.path.abspath(BACKGROUND_FOLDER)
        print(f"Current working directory: {os.getcwd()}")
        print(f"Checking if folder exists: {folder_path}")

        if os.path.exists(folder_path):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(folder_path)
                elif os.name == 'posix':
                    if sys.platform == 'darwin':  # macOS
                        subprocess.call(['open', folder_path])
                    else:  # Linux
                        subprocess.call(['xdg-open', folder_path])
            except Exception as e:
                print(f"Failed to open folder: {e}")
        else:
            print(f"Folder does not exist: {folder_path}")

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
        self.clearLayout(layout)
        row, col, max_cols = 0, 0, 2  # Устанавливаем количество столбцов
        for file_name, file_path in photos:
            containerWidget = QWidget()
            formLayout = QFormLayout(containerWidget)
            formLayout.setVerticalSpacing(5)

            pixmap = QPixmap(file_path)
            imageLabel = QLabel()
            imageLabel.setPixmap(pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
            imageLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
            imageLabel.mousePressEvent = self.onImageClicked(file_path)

            textLabel = QLabel(file_name)
            textLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

            formLayout.addRow(imageLabel)
            formLayout.addRow(textLabel)
            layout.addWidget(containerWidget, row, col)

            col += 1
            if col >= max_cols:
                col = 0
                row += 1


    def onImageClicked(self, photo):
        def handler(event):
            global BUFFER_DATA
            BUFFER_DATA[self.key]['background']['name'] = photo
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
        global BUFFER_DATA
        fileName, _ = QFileDialog.getOpenFileName(self, "Open file", "", "JSON files (*.json)")
        if fileName:
            try:
                with open(fileName, "r", encoding="utf-8") as file:
                    BUFFER_DATA = json.load(file)
                    self.dockTreeWidget(BUFFER_DATA)
            except Exception as e:
                QMessageBox.critical(self, "Load Error", f"Failed to load file: {e}")

    def toolbar(self):
        toolbar = QToolBar("Tool bar")
        self.addToolBar(toolbar)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: rgb(30, 40, 50);
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
        addSprite.triggered.connect(self.openSpriteWindow)

        self.toolbar = toolbar

    def openSpriteWindow(self):
        global SPRITES_FOLDER
        SPRITES_FOLDER = "sprites/basic"
        key = self.path[0] if hasattr(self, 'path') and self.path else None
        if key:
            self.spriteWindow = SpriteWindow(key, None)
            self.spriteWindow.exec()

    def openBackgroundWindow(self):
        key = self.path[0] if hasattr(self, 'path') and self.path else None
        if key:
            self.backgroundWindow = BackgroundWindow(key)
            self.backgroundWindow.exec()

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
        try:
            for key, value in data.items():
                print(f"Processing key: {key}")  # Логирование обрабатываемого ключа
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

                if "animation" in value["background"] and value["background"]["animation"]:
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

                if "count" in value["sprites"] and value["sprites"]["count"] > 0:
                    spriteArr = []
                    sprite_count = value["sprites"]["count"]  # Получение количества спрайтов
                    for v in range(sprite_count):
                        sprite_key = str(v)  # Генерация ключа в виде строки
                        print(f"Processing sprite key: {sprite_key}")  # Логирование обрабатываемого ключа спрайта
                        if sprite_key in value["sprites"]:
                            spriteArr.append(QTreeWidgetItem([f"sprite {v + 1}"]))
                            sprites.addChild(spriteArr[v])

                            spriteArr[v].addChild(QTreeWidgetItem(["name"]))
                            spriteArr[v].addChild(QTreeWidgetItem(["position"]))
                            spriteArr[v].addChild(QTreeWidgetItem(["scale"]))

                            if "animation" in value["sprites"][sprite_key] and value["sprites"][sprite_key]["animation"]:
                                animation_item = QTreeWidgetItem(["animation"])
                                spriteArr[v].addChild(animation_item)
                                animation_item.addChild(QTreeWidgetItem(["time"]))
                                animation_item.addChild(QTreeWidgetItem(["position"]))
                                animation_item.addChild(QTreeWidgetItem(["scale"]))
                            else:
                                spriteArr[v].addChild(QTreeWidgetItem(["animation"]))
                        else:
                            print(f"KeyError: Sprite key {sprite_key} not found in sprites")  # Логирование отсутствующего ключа
        except KeyError as e:
            print(f"KeyError: {e}")
        except TypeError as e:
            print(f"TypeError: {e}")
        except Exception as e:
            print(f"Unexpected error: {e}")


    def dockTreeWidget(self, data):
        try:
            self.treeWidget.clear()
            self.loadTreeItems(data)
        except Exception as e:
            print(f"Error in dockTreeWidget: {e}")


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
        global BUFFER_DATA
        layout = self.inspectorGroup.layout()
        # Очистка предыдущих виджетов
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        key = path[0]
        formLayout = QFormLayout()
        scrollArea = QScrollArea()
        scrollAreaWidget = QWidget()
        scrollAreaWidget.setLayout(formLayout)
        scrollArea.setWidget(scrollAreaWidget)
        scrollArea.setWidgetResizable(True)

        layout.addWidget(scrollArea)

        background = [QPushButton("Select"), QSpinBox(), QSpinBox(), 
                      QDoubleSpinBox(), QDoubleSpinBox(), QCheckBox("off"), 
                      [QSpinBox(), QSpinBox(), QSpinBox(), QDoubleSpinBox(), QDoubleSpinBox()]]
        
        text = [QComboBox(), QTextEdit()]

        ui = [QComboBox(), QLineEdit(), QPushButton("Select")]

        music = [QListWidget(), QPushButton("add"), QPushButton("delete"), QCheckBox("off")]

        backgroundItem = QLabel("Background")

        formLayout.addRow(backgroundItem)

        backgroundImage = QLabel("Background image")
        backgroundImage.setStyleSheet("padding-left: 20px;")

        backgroundPosition = QLabel("Position")
        backgroundPosition.setStyleSheet("padding-left: 20px;")

        backgroundScale = QLabel("Scale")
        backgroundScale.setStyleSheet("padding-left: 20px;")

        backgroundAnimationButton = QLabel("Animation")
        backgroundAnimationButton.setStyleSheet("padding-left: 20px;")

        backgroundPositionLayout = QHBoxLayout()
        backgroundScaleLayout = QHBoxLayout()
        backgroundAnimationButtonLayout = QHBoxLayout()

        background[1].setMaximum(10000)
        background[2].setMaximum(10000)
        background[3].setMaximum(10000)
        background[4].setMaximum(10000)

        background[1].setValue(BUFFER_DATA[key]['background']['position']['x'])
        background[1].setRange(0,10000)
        background[2].setValue(BUFFER_DATA[key]['background']['position']['y'])
        background[2].setRange(0,10000)

        background[3].setValue(BUFFER_DATA[key]['background']['scale']['x'])
        background[4].setValue(BUFFER_DATA[key]['background']['scale']['y'])

        background[5].setChecked(BUFFER_DATA[key]['background']['animation'])

        backgroundPositionLayout.addWidget(backgroundPosition)
        backgroundPositionLayout.addWidget(QLabel("X"))
        backgroundPositionLayout.addWidget(background[1])
        backgroundPositionLayout.addWidget(QLabel("Y"))
        backgroundPositionLayout.addWidget(background[2])

        backgroundScaleLayout.addWidget(backgroundScale)
        backgroundScaleLayout.addWidget(QLabel("X"))
        backgroundScaleLayout.addWidget(background[3])
        backgroundScaleLayout.addWidget(QLabel("Y"))
        backgroundScaleLayout.addWidget(background[4])

        backgroundAnimationButtonLayout.addWidget(backgroundAnimationButton)
        backgroundAnimationButtonLayout.addWidget(background[5])

        formLayout.addRow(backgroundImage, background[0])
        formLayout.addRow(backgroundPositionLayout)
        formLayout.addRow(backgroundScaleLayout)
        formLayout.addRow(backgroundAnimationButtonLayout)

        if BUFFER_DATA[key]['background']['name'] != '':
            background[0].setText(BUFFER_DATA[key]['background']['name'][12:])

        background[5].toggled.connect(lambda: self.togledBackgroundAnimationButton(background[5], BUFFER_DATA, key, path))
        background[0].clicked.connect(lambda: self.selectBackground())
        
        if background[5].isChecked():
            background[5].setText("on")

            backgroundAnimationTime = QLabel("Animation time")
            backgroundAnimationTime.setStyleSheet("padding-left: 20px;")

            backgroundAnimationPosition = QLabel("Position")
            backgroundAnimationPosition.setStyleSheet("padding-left: 20px;")

            backgroundAnimationScale = QLabel("Scale")
            backgroundAnimationScale.setStyleSheet("padding-left: 20px;")

            backgroundAnimationTimeLayout = QHBoxLayout()
            backgroundAnimationPositionLayout = QHBoxLayout()
            backgroundAnimationScaleLayout = QHBoxLayout()

            background[6][0].setValue(BUFFER_DATA[key]['background']['animationSettings']['time'])
            background[6][0].setRange(0,10000)
            background[6][1].setValue(BUFFER_DATA[key]['background']['animationSettings']['position']['x'])
            background[6][1].setRange(-10000,10000)
            background[6][2].setValue(BUFFER_DATA[key]['background']['animationSettings']['position']['y'])
            background[6][2].setRange(-10000,10000)
            background[6][3].setValue(BUFFER_DATA[key]['background']['animationSettings']['scale']['x'])
            background[6][4].setValue(BUFFER_DATA[key]['background']['animationSettings']['scale']['y'])

            backgroundAnimationTimeLayout.addWidget(backgroundAnimationTime)
            backgroundAnimationTimeLayout.addWidget(background[6][0])

            backgroundAnimationPositionLayout.addWidget(backgroundAnimationPosition)
            backgroundAnimationPositionLayout.addWidget(QLabel('X'))
            backgroundAnimationPositionLayout.addWidget(background[6][1])
            backgroundAnimationPositionLayout.addWidget(QLabel('Y'))
            backgroundAnimationPositionLayout.addWidget(background[6][2])

            backgroundAnimationScaleLayout.addWidget(backgroundAnimationScale)
            backgroundAnimationScaleLayout.addWidget(QLabel("X"))
            backgroundAnimationScaleLayout.addWidget(background[6][3])
            backgroundAnimationScaleLayout.addWidget(QLabel("Y"))
            backgroundAnimationScaleLayout.addWidget(background[6][4])

            formLayout.addRow(backgroundAnimationTimeLayout)
            formLayout.addRow(backgroundAnimationPositionLayout)
            formLayout.addRow(backgroundAnimationScaleLayout)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        formLayout.addRow(line)

        background[2].valueChanged.connect(partial(self.saveSpinValue, background[2], '', 'y', BUFFER_DATA, 'position', key))
        background[1].valueChanged.connect(partial(self.saveSpinValue, background[1], '', 'x', BUFFER_DATA, 'position', key))
        background[3].valueChanged.connect(partial(self.saveSpinValue, background[3], '', 'x', BUFFER_DATA, 'scale', key))
        background[4].valueChanged.connect(partial(self.saveSpinValue, background[4], '', 'y', BUFFER_DATA, 'scale', key))
        background[6][0].valueChanged.connect(partial(self.saveSpinValue, background[6][0], 'animationSettings', '', BUFFER_DATA, 'time', key))
        background[6][1].valueChanged.connect(partial(self.saveSpinValue, background[6][1], 'animationSettings', 'x', BUFFER_DATA, 'position', key))
        background[6][2].valueChanged.connect(partial(self.saveSpinValue, background[6][2], 'animationSettings', 'y', BUFFER_DATA, 'position', key))
        background[6][3].valueChanged.connect(partial(self.saveSpinValue, background[6][3], 'animationSettings', 'x', BUFFER_DATA, 'scale', key))
        background[6][4].valueChanged.connect(partial(self.saveSpinValue, background[6][4], 'animationSettings', 'y', BUFFER_DATA, 'scale', key))

        formLayout.addRow(QLabel('Text'))
        charaList = ['select chara', 'Макиширо Ямагаки', 'Рина Микура', 'Саймон Мацуда', 'Рэйчел Асамая', 'Мишель Мурамаки',
                     'Сэмми Коуда', 'Мичио Хаякава', 'Сегикадзе Харада', 'Дайчиро Катаяма', 'Цукико Аска',
                     'Амайя Накагава', "Румико Сакаи", 'Крис Лайтер', 'Янн Ёсимура', 'Тору Ёкояма', 'Катсураги Танабэ',
                     'Монораку', 'advanced']

        text[0].addItems(charaList)


        text[0].setStyleSheet("""
            QComboBox QAbstractItemView {
                color: rgb(85, 170, 255);	
                background-color: #373e4e;
                padding: 10px;
                selection-background-color: white;
            }
            """)


        charaListLayout = QHBoxLayout()

        charaListLabel = QLabel('Character')
        charaListLabel.setStyleSheet("padding-left: 20px;")

        charaListLayout.addWidget(charaListLabel)
        charaListLayout.addWidget(text[0])

        formLayout.addRow(charaListLayout)


        if BUFFER_DATA[key]['text']['charaName'] != '':
            try:
                index = charaList.index(BUFFER_DATA[key]['text']['charaName'])
                if index == 18:
                    text[0].setCurrentIndex(index)
                    self.lineEdit('',formLayout, key) 
                else:
                    text[0].setCurrentIndex(index)
            except:
                index = 18
                text[0].setCurrentIndex(index)
                self.lineEdit(BUFFER_DATA[key]['text']['charaName'],formLayout, key)    
        elif BUFFER_DATA[key]['text']['charaName'] == '':
            index = 0
            text[0].setCurrentIndex(index)

        text[0].currentIndexChanged.connect(lambda: self.charaTextName(text[0],key,path))


        textLayout = QHBoxLayout()

        textLabel = QLabel('text')
        textLabel.setStyleSheet("padding-left: 20px;")

        textLayout.addWidget(textLabel)
        textLayout.addWidget(text[1])

        formLayout.addRow(textLayout)

        text[1].setMaximumSize(500, 100)

        if BUFFER_DATA[key]['text']['text'] != '':
            text[1].setText(BUFFER_DATA[key]['text']['text'])



        text[1].textChanged.connect(lambda: self.saveText(text[1].toPlainText(), key))
        formLayout.addRow(line)

        formLayout.addRow(QLabel('UI'))

        timeOfDayLayout = QHBoxLayout()
        timeOfDayLabel = QLabel("Time of day")
        timeOfDayLabel.setStyleSheet("padding-left: 20px;")
        timeList = ["select", "Morning", "Afternoon", "Evening", "Night"]

        ui[0].addItems(timeList)

        timeOfDayLayout.addWidget(timeOfDayLabel)
        timeOfDayLayout.addWidget(ui[0])

        ui[0].setStyleSheet("""
            QComboBox QAbstractItemView {
                color: rgb(85, 170, 255);	
                background-color: #373e4e;
                padding: 10px;
                selection-background-color: white;
            }
            """)

        formLayout.addRow(timeOfDayLayout)

        if BUFFER_DATA[key]['ui']['time'] != '':
            try:
                index = timeList.index(BUFFER_DATA[key]['ui']['time'])
                ui[0].setCurrentIndex(index)
            except:
                BUFFER_DATA[key]['ui']['time'] = ''
                ui[0].setCurrentIndex(0)
        else:
            ui[0].setCurrentIndex(0)

        ui[0].currentIndexChanged.connect(lambda: self.timeOfDaySave(ui[0], key))
        

        chapterLayout = QHBoxLayout()

        chapterLabel = QLabel('Chapter')
        chapterLabel.setStyleSheet("padding-left: 20px;")

        chapterLayout.addWidget(chapterLabel)
        chapterLayout.addWidget(ui[1])

        if BUFFER_DATA[key]['ui']['chapter'] == '':
            try:
                BUFFER_DATA[key]['ui']['chapter'] = BUFFER_DATA[str(int(key) - 1)]['ui']['chapter']
                ui[1].setText(BUFFER_DATA[str(int(key) - 1)]['ui']['chapter'])
            except:
                BUFFER_DATA[key]['ui']['chapter'] = ''
                ui[1].setText('')
        else:
            ui[1].setText(BUFFER_DATA[key]['ui']['chapter'])

        formLayout.addRow(chapterLayout)

        ui[1].textChanged.connect(lambda: self.saveChapter(ui[1].text,key))

        charaEmotionLayout = QHBoxLayout()
        charaEmotionLabel = QLabel('Chara emotion')
        charaEmotionLabel.setStyleSheet("padding-left: 20px;")

        charaEmotionLayout.addWidget(charaEmotionLabel)
        charaEmotionLayout.addWidget(ui[2])

        formLayout.addRow(charaEmotionLayout)

        ui[2].clicked.connect(self.openHeroEmotionWindow)

        if 'charaEmotion' not in BUFFER_DATA[key]['ui']:
            BUFFER_DATA[key]['ui']['charaEmotion'] = ''
            
        if BUFFER_DATA[key]['ui']['charaEmotion'] == '':
            ui[2].setText('select')
        else:
            ui[2].setText(BUFFER_DATA[key]['ui']['charaEmotion'])


        formLayout.addRow(line)

        formLayout.addRow(QLabel('Sprites'))        

        

        self.spritesListWidget = QListWidget()

        self.spritesListWidget.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        self.spriteList = []

        self.spriteListCount = int(BUFFER_DATA[key]['sprites']['count'])

        if  self.spriteListCount > 0:
            for i in range(0, self.spriteListCount):
            
                if BUFFER_DATA[key]['sprites'][str(i)]['objectName'] != '':
                    item = QListWidgetItem(BUFFER_DATA[key]['sprites'][str(i)]['objectName'])
                else:
                    item = QListWidgetItem(f'Sprite: {i}')
                    BUFFER_DATA[key]['sprites'][str(i)]['objectName'] = f'Sprite: {i}'

                self.spriteList.append(i)
                self.spritesListWidget.addItem(item)

        spritesLayout = QHBoxLayout()
        spritesLabel = QLabel('Sprite hierarchy')
        spritesLabel.setStyleSheet("padding-left: 20px;")
        spritesLayout.addWidget(spritesLabel)
        spritesLayout.addWidget(self.spritesListWidget)
        

        formLayout.addRow(spritesLayout)

        self.spritesListWidget.setMaximumHeight(300)


        self.spritesListWidget.model().rowsMoved.connect(lambda: self.changeSpriteList(key))

        self.spritesListWidget.itemClicked.connect(partial(self.layoutChecker, formLayout, key))

        self.formLayout = formLayout
    
    def sptiteSettings(self, item, key, formLayout):

        self.spriteLayout = QFormLayout()
        layout = self.spriteLayout

        self.item = item
        index = str(self.spritesListWidget.row(item))


        spriteSelectLabel = QLabel("Sprite")
        spriteSelectLabel.setStyleSheet("padding-left: 20px;")
        spriteSelectButton = QPushButton("select")
        spriteSelectButton.setMinimumWidth(200)
        spriteSelectButton.setMaximumWidth(200)
        spriteSelectLayout = QHBoxLayout()
        spriteSelectLayout.addWidget(spriteSelectLabel)
        spriteSelectLayout.addWidget(spriteSelectButton)

        self.spriteSelectButton = spriteSelectButton

        layout.addRow(spriteSelectLayout)

        spriteSelectButton.clicked.connect(self.openSpriteSelectWindow)

        
        if BUFFER_DATA[key]['sprites'][index]['name'] == '':
            spriteSelectButton.setText("select")
        else:
            spriteSelectButton.setText(BUFFER_DATA[key]['sprites'][str(self.spritesListWidget.row(item))]['name'])

        self.key = key
        self.index = index

        positionLayout = QHBoxLayout()
        positionLabel = QLabel('Position')
        positionLabel.setStyleSheet("padding-left: 20px;")
        positionXSpinbox = QSpinBox()
        positionYSpinbox = QSpinBox()
        positionLayout.addWidget(positionLabel)
        positionLayout.addWidget(QLabel('X'))
        positionLayout.addWidget(positionXSpinbox)
        positionLayout.addWidget(QLabel('Y'))
        positionLayout.addWidget(positionYSpinbox)

        layout.addRow(positionLayout)

        positionXSpinbox.setRange(-10000, 10000)
        positionXSpinbox.setValue(BUFFER_DATA[key]["sprites"][index]["position"]["x"])
        positionYSpinbox.setRange(-10000, 10000)
        positionYSpinbox.setValue(BUFFER_DATA[key]["sprites"][index]["position"]["y"])
        #TODO

        scaleLayout = QHBoxLayout()
        scaleLabel = QLabel('Scale')
        scaleLabel.setStyleSheet("padding-left: 20px;")
        scaleXSpinbox = QDoubleSpinBox()
        scaleYSpinbox = QDoubleSpinBox()
        scaleLayout.addWidget(scaleLabel)
        scaleLayout.addWidget(QLabel('X'))
        scaleLayout.addWidget(scaleXSpinbox)
        scaleLayout.addWidget(QLabel('Y'))
        scaleLayout.addWidget(scaleYSpinbox)

        layout.addRow(scaleLayout)

        scaleYSpinbox.setValue(BUFFER_DATA[key]["sprites"][index]["scale"]["x"])
        scaleYSpinbox.setValue(BUFFER_DATA[key]["sprites"][index]["scale"]["y"])
        #TODO

        animationLayout = QHBoxLayout()
        animationLabel = QLabel('Animation')
        animationLabel.setStyleSheet("padding-left: 20px;")
        animationQcheckbox = QCheckBox('off')
        animationLayout.addWidget(animationLabel)
        animationLayout.addWidget(animationQcheckbox)

        layout.addRow(animationLayout)

        if BUFFER_DATA[key]['sprites'][index]['animation'] == True:
            animationQcheckbox.setText('on')
            animationQcheckbox.setChecked(True)

            timeLayout = QHBoxLayout()
            timeLabel = QLabel('Animation time')
            timeLabel.setStyleSheet("padding-left: 20px;")
            timeSpinbox = QSpinBox()
            timeLayout.addWidget(timeLabel)
            timeLayout.addWidget(timeSpinbox)

            layout.addRow(timeLayout)

            timeSpinbox.setRange(0,10000)
            timeSpinbox.setValue(BUFFER_DATA[key]["sprites"][index]["animationSettings"]["time"])
            #TODO

            animationPositionLayout = QHBoxLayout()
            animationPositionLabel = QLabel('Position')
            animationPositionLabel.setStyleSheet("padding-left: 20px;")
            animationPositionXSpinbox = QSpinBox()
            animationPositionYSpinbox = QSpinBox()
            animationPositionLayout.addWidget(animationPositionLabel)
            animationPositionLayout.addWidget(QLabel('X'))
            animationPositionLayout.addWidget(animationPositionXSpinbox)
            animationPositionLayout.addWidget(QLabel('Y'))
            animationPositionLayout.addWidget(animationPositionYSpinbox)

            layout.addRow(animationPositionLayout)
            animationPositionXSpinbox.setRange(-10000,10000)
            animationPositionYSpinbox.setRange(-10000,10000)
            animationPositionXSpinbox.setValue(BUFFER_DATA[key]["sprites"][index]["animationSettings"]["position"]["x"])
            animationPositionYSpinbox.setValue(BUFFER_DATA[key]["sprites"][index]["animationSettings"]["position"]["y"])
            #TODO

            animationScaleLayout = QHBoxLayout()
            animationScaleLabel = QLabel('Scale')
            animationScaleLabel.setStyleSheet("padding-left: 20px;")
            animationScaleXSpinbox = QSpinBox()
            animationScaleYSpinbox = QSpinBox()
            animationScaleLayout.addWidget(animationScaleLabel)
            animationScaleLayout.addWidget(QLabel('X'))
            animationScaleLayout.addWidget(animationScaleXSpinbox)
            animationScaleLayout.addWidget(QLabel('Y'))
            animationScaleLayout.addWidget(animationScaleYSpinbox)

            layout.addRow(animationScaleLayout)

            #TODO

        animationQcheckbox.toggled.connect(lambda: self.switchSpriteAnimation(key, item, animationQcheckbox, formLayout))
        self.index = str(self.spritesListWidget.row(item))

    def openSpriteSelectWindow(self):
        self.changeSpriteWindow = SpriteWindow(self.key, self.index)
        self.changeSpriteWindow.sprite.connect(self.onSpriteSelect)
        self.changeSpriteWindow.exec()

    def onSpriteSelect(self, selectedImage):
        
        key = self.path[0] if hasattr(self, 'path') and self.path else None
        
        BUFFER_DATA[key]['sprites'][self.index]['name'] = selectedImage
        self.spriteSelectButton.setText(selectedImage)

        self.layoutChecker(self.formLayout, self.key, self.item)
            
        




    def switchSpriteAnimation(self, key, item, checkbox, formLayout):
        

        if checkbox.isChecked():
            BUFFER_DATA[key]['sprites'][self.index]['animation'] = True
            BUFFER_DATA[key]['sprites'][self.index]['animationSettings'] = {
                "time": 0,
                "position":{
                    "x": 0,
                    "y": 0
                },
                "scale":{
                    "x": 1,
                    "y": 1
                }
            }
        else:
            BUFFER_DATA[key]['sprites'][self.index]['animation'] = False
            if 'animationSettings' in BUFFER_DATA[key]['sprites'][self.index]:
                del BUFFER_DATA[key]['sprites'][self.index]['animationSettings']
            

        self.layoutChecker(formLayout, key, item)

    def layoutChecker(self, layout, key, item):
        try:
            self.spriteLayout.deleteLater()
            self.sptiteSettings(item, key, layout)
        except:
            self.sptiteSettings(item, key, layout)
        layout.addRow(self.spriteLayout)


    def saveSpritelist(self, key):
        sprite_order = [self.spritesListWidget.item(i).text() for i in range(self.spritesListWidget.count())]
        sprite_count = int(BUFFER_DATA[key]['sprites']['count'])
        buffer = BUFFER_DATA[key]['sprites']
        updated_sprites = {'count': sprite_count}

        original_indices = {buffer[str(i)]['objectName']: i for i in range(sprite_count)}

        for new_index, object_name in enumerate(sprite_order):
            original_index = original_indices[object_name]
            updated_sprites[str(new_index)] = buffer[str(original_index)]

        BUFFER_DATA[key]['sprites'] = updated_sprites
        self.inspectorLoad(self.path)


    def  changeSpriteList(self, key):
        self.spriteList.clear()  
        count = self.spritesListWidget.count()
        for i in range(count):
            item = self.spritesListWidget.item(i)
            self.spriteList.append(item.text()) 
        self.saveSpritelist(key)

    def openHeroEmotionWindow(self):
        self.heroEmotionWindow = SelectMainHeroEmotion()
        self.heroEmotionWindow.emotionSelected.connect(self.onHeroEmotionSelected)
        self.heroEmotionWindow.exec()

    def onHeroEmotionSelected(self, selected_image):
        print(f"Selected image: {selected_image}")
        key = self.path[0] if hasattr(self, 'path') and self.path else None
        if key:
            BUFFER_DATA[key]['ui']['charaEmotion'] = selected_image
            self.inspectorLoad(self.path)

    def saveChapter(self, text, key):
        BUFFER_DATA[key]['ui']['chapter'] = text

    def timeOfDaySave(self, qbox, key):
        text = qbox.currentText()
        BUFFER_DATA[key]['ui']['time'] = text
        
    def saveText(self, text, key):
        BUFFER_DATA[key]['text']['text'] = text

    def lineEditSave(self,text,key):
        BUFFER_DATA[key]['text']['charaName'] = text

    def lineEdit(self, text, layout, key):
        textLayout = QHBoxLayout()
        textName = QLabel("advanced name")
        textLineEdit = QLineEdit(text)

        textName.setStyleSheet("padding-left: 20px;")

        textLayout.addWidget(textName)
        textLayout.addWidget(textLineEdit)

        layout.addRow(textLayout)
        textLineEdit.textChanged.connect(lambda: self.lineEditSave(text, key))

    def charaTextName(self,qbox,key,path):
        text = qbox.currentText()
        BUFFER_DATA[key]['text']['charaName'] = text
        self.inspectorLoad(path)

    def saveSpinValue(self, spinbox, key1, key3, data, key2, key0):
        if key1 != '' and key3 != '':
            data[key0]['background'][key1][key2][key3] = spinbox.value()
        elif key1 != '' and key3 == '':
            data[key0]['background'][key1][key2] = spinbox.value()
        elif key1 == '':
            data[key0]['background'][key2][key3] = spinbox.value()

    def togledBackgroundAnimationButton(self, checkbox, data, key, path):
        if checkbox.isChecked():
            data[key]['background']['animation'] = True
            data[key]['background']['animationSettings'] = {
                "time": 0,
                "position":{
                    "x": 0,
                    "y": 0
                },
                "scale":{
                    "x": 1,
                    "y": 1
                }
            }
        else:
            data[key]['background']['animation'] = False
            if 'animationSettings' in data[key]['background']:
                del data[key]['background']['animationSettings']
        
        self.inspectorLoad(path)

    def selectBackground(self):
        key = self.path[0] if hasattr(self, 'path') and self.path else None
        if key:
            self.backgroundWindow = BackgroundWindow(key)
            self.backgroundWindow.exec()
        self.inspectorLoad(self.path)

            

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())