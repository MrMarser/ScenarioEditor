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
from PyQt6.QtCore import QEvent, Qt, pyqtSignal

BACKGROUND_FOLDER = "backgrounds/"
SPRITES_FOLDER = "sprites/basic"
MAIN_HERO_EMOTION_FOLDER = "sprites/makishiro"

# Example structure
BUFFER_DATA = {
    "scene1": {
        "background": {"name": "", "position": {"x": 0, "y": 0}, "scale": {"x": 1, "y": 1}, "animation": False},
        "text": {"charaName": "", "text": ""},
        "ui": {"time": "", "chapter": "", "charaEmotion": ""},
        "sprite": {"count": 0}  # Ensure this is initialized
    }
}

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
    spriteSelected = pyqtSignal(str)  # Сигнал для передачи выбранного спрайта

    def __init__(self, key, spriteId):
        self.spriteId = spriteId
        self.key = key
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
                # Check if the sprite structure exists
                if self.key not in BUFFER_DATA:
                    print(f"Error: Key '{self.key}' not found in BUFFER_DATA")
                    return
                
                if "sprite" not in BUFFER_DATA[self.key]:
                    print(f"Error: 'sprite' key not found in BUFFER_DATA[{self.key}]")
                    return
                
                if self.spriteId is None:
                    count = BUFFER_DATA[self.key]["sprite"]["count"]
                    BUFFER_DATA[self.key]["sprite"]["count"] = count + 1
                    BUFFER_DATA[self.key]["sprite"][str(count)] = {"spriteId": "",
                                                                   "name": file_path,
                                                                   "position": {
                                                                       "x": 0,
                                                                       "y": 0
                                                                   },
                                                                   "scale": {
                                                                       "x": 1,
                                                                       "y": 1
                                                                   },
                                                                   "animation": False}
                    
                else:
                    # Ensure spriteId exists
                    if str(self.spriteId) not in BUFFER_DATA[self.key]["sprite"]:
                        print(f"Error: spriteId '{self.spriteId}' not found in BUFFER_DATA[{self.key}]['sprite']")
                        return
                    
                    BUFFER_DATA[self.key]["sprite"][str(self.spriteId)]["name"] = file_path
                
                SPRITES_FOLDER = BUFFER_SPRITES_FOLDER
                self.spriteSelected.emit(file_path)  # Эмиссия сигнала
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

        self.key = None  # Initialize self.key to None

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

        # Use a lambda to defer the method call
        addSprite.triggered.connect(lambda: self.openSpriteWindow(self.key, None))  

        self.toolbar = toolbar

    def openSpriteWindow(self, key, spriteId):
        global SPRITES_FOLDER
        SPRITES_FOLDER = "sprites/basic"
        if key:
            self.spriteWindow = SpriteWindow(key, spriteId)
            self.spriteWindow.spriteSelected.connect(self.onSpriteSelected)  # Подключение сигнала к слоту
            self.spriteWindow.exec()

    def onSpriteSelected(self, sprite_path):
        # Логика обновления QListWidget
        key = self.path[0] if hasattr(self, 'path') and self.path else None
        if key:
            self.inspectorLoad(self.path)  # Перезагрузка инспектора

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
        self.key = key

        formLayout = QFormLayout()
        scrollArea = QScrollArea()
        scrollAreaWidget = QWidget()
        scrollAreaWidget.setLayout(formLayout)
        scrollArea.setWidget(scrollAreaWidget)
        scrollArea.setWidgetResizable(True)

        layout.addWidget(scrollArea)

        formLayout.addRow(QLabel("Background"))

        backgroundSelectLayout = QHBoxLayout()
        backgroundSelectLabel = QLabel("Select background")
        backgroundSelectLabel.setStyleSheet("padding-left: 20px;")
        backgroundSelectButton = QPushButton()
        
        backgroundSelectLayout.addWidget(backgroundSelectLabel)
        backgroundSelectLayout.addWidget(backgroundSelectButton)

        formLayout.addRow(backgroundSelectLayout)

        if BUFFER_DATA[key]["background"]["name"] != "":
            backgroundSelectButtonText = BUFFER_DATA[key]["background"]["name"]
            backgroundSelectButton.setText(backgroundSelectButtonText.replace("backgrounds/", ""))
        else:
            backgroundSelectButton.setText("Select")

        backgroundSelectButton.clicked.connect(lambda: self.selectBackground())

        backgroundPositionLayout = QHBoxLayout()
        backgroundPositionLabel = QLabel("Position")
        backgroundPositionLabel.setStyleSheet("padding-left: 20px;")
        backgroundPositionX = QSpinBox()
        backgroundPositionY = QSpinBox()

        backgroundPositionLayout.addWidget(backgroundPositionLabel)
        backgroundPositionLayout.addWidget(QLabel("X"))
        backgroundPositionLayout.addWidget(backgroundPositionX)
        backgroundPositionLayout.addWidget(QLabel("Y"))
        backgroundPositionLayout.addWidget(backgroundPositionY)

        formLayout.addRow(backgroundPositionLayout)

        backgroundPositionX.setRange(-10000, 10000)
        backgroundPositionY.setRange(-10000, 10000)

        backgroundPositionX.setValue(BUFFER_DATA[key]['background']['position']['x'])
        backgroundPositionY.setValue(BUFFER_DATA[key]['background']['position']['y'])

        backgroundPositionX.valueChanged.connect(lambda: self.saveSpinValue(backgroundPositionX, key, False, "position", "x", "background", None))
        backgroundPositionY.valueChanged.connect(lambda: self.saveSpinValue(backgroundPositionY, key, False, "position", "y", "background", None))

        backgroundScaleLayout = QHBoxLayout()
        backgroundScaleLabel = QLabel("Scale")
        backgroundScaleLabel.setStyleSheet("padding-left: 20px;")
        backgroundScaleX = QDoubleSpinBox()
        backgroundScaleY = QDoubleSpinBox()

        backgroundScaleLayout.addWidget(backgroundScaleLabel)
        backgroundScaleLayout.addWidget(QLabel("X"))
        backgroundScaleLayout.addWidget(backgroundScaleX)
        backgroundScaleLayout.addWidget(QLabel("Y"))
        backgroundScaleLayout.addWidget(backgroundScaleY)

        formLayout.addRow(backgroundScaleLayout)

        backgroundScaleX.setRange(-10000, 10000)
        backgroundScaleY.setRange(-10000, 10000)

        backgroundScaleX.setValue(BUFFER_DATA[key]['background']['scale']['x'])
        backgroundScaleY.setValue(BUFFER_DATA[key]['background']['scale']['y'])

        backgroundScaleX.valueChanged.connect(lambda: self.saveSpinValue(backgroundScaleX, key, False, "scale", "x", "background", None))
        backgroundScaleY.valueChanged.connect(lambda: self.saveSpinValue(backgroundScaleY, key, False, "scale", "y", "background", None))

        backgroundAnimationLayout = QHBoxLayout()
        backgroundAnimationLabel = QLabel("Animation")
        backgroundAnimationLabel.setStyleSheet("padding-left: 20px;")
        backgroundAnimationCheckbox = QCheckBox()

        backgroundAnimationLayout.addWidget(backgroundAnimationLabel)
        backgroundAnimationLayout.addWidget(backgroundAnimationCheckbox)

        formLayout.addRow(backgroundAnimationLayout)

        if BUFFER_DATA[key]["background"]["animation"] == True:
            backgroundAnimationCheckbox.setChecked(True)

        backgroundAnimationTimeLayout = QHBoxLayout()
        backgroundAnimationTimeLabel = QLabel("Animation time")
        backgroundAnimationTimeLabel.setStyleSheet("padding-left: 20px;")
        backgroundAnimationTime = QSpinBox()

        backgroundAnimationTimeLayout.addWidget(backgroundAnimationTimeLabel)
        backgroundAnimationTimeLayout.addWidget(backgroundAnimationTime)

        formLayout.addRow(backgroundAnimationTimeLayout)

        backgroundAnimationTime.setRange(0, 10000)
        backgroundAnimationTime.setToolTip("in 1 sec 60 units")

        backgroundAnimationTime.valueChanged.connect(lambda: self.saveSpinValue(backgroundAnimationTime, key, True, "time", None, "background", None))

        backgroundAnimationPositionLayout = QHBoxLayout()
        backgroundAnimationPositionLabel = QLabel("Position")
        backgroundAnimationPositionLabel.setStyleSheet("padding-left: 20px;")
        backgroundAnimationPositionX = QSpinBox()
        backgroundAnimationPositionY = QSpinBox()

        backgroundAnimationPositionLayout.addWidget(backgroundAnimationPositionLabel)
        backgroundAnimationPositionLayout.addWidget(QLabel("X"))
        backgroundAnimationPositionLayout.addWidget(backgroundAnimationPositionX)
        backgroundAnimationPositionLayout.addWidget(QLabel("Y"))
        backgroundAnimationPositionLayout.addWidget(backgroundAnimationPositionY)

        formLayout.addRow(backgroundAnimationPositionLayout)

        backgroundAnimationPositionX.setRange(-10000, 10000)
        backgroundAnimationPositionY.setRange(-10000, 10000)

        backgroundAnimationPositionX.valueChanged.connect(lambda: self.saveSpinValue(backgroundAnimationPositionX, key, True, "position", "x", "background", None))
        backgroundAnimationPositionY.valueChanged.connect(lambda: self.saveSpinValue(backgroundAnimationPositionY, key, True, "position", "y", "background", None))

        backgroundAnimationScaleLayout = QHBoxLayout()
        backgroundAnimationScaleLabel = QLabel("Scale")
        backgroundAnimationScaleLabel.setStyleSheet("padding-left: 20px;")
        backgroundAnimationScaleX = QDoubleSpinBox()
        backgroundAnimationScaleY = QDoubleSpinBox()

        backgroundAnimationScaleLayout.addWidget(backgroundAnimationScaleLabel)
        backgroundAnimationScaleLayout.addWidget(QLabel("X"))
        backgroundAnimationScaleLayout.addWidget(backgroundAnimationScaleX)
        backgroundAnimationScaleLayout.addWidget(QLabel("Y"))
        backgroundAnimationScaleLayout.addWidget(backgroundAnimationScaleY)

        formLayout.addRow(backgroundAnimationScaleLayout)

        backgroundAnimationScaleX.setRange(0, 10000)
        backgroundAnimationScaleY.setRange(0, 10000)

        backgroundAnimationScaleX.valueChanged.connect(lambda: self.saveSpinValue(backgroundAnimationScaleX, key, True, "scale", "x", "background", None))
        backgroundAnimationScaleY.valueChanged.connect(lambda: self.saveSpinValue(backgroundAnimationScaleY, key, True, "scale", "y", "background", None))
        
        if 'animationSettings' in BUFFER_DATA[key]["background"]:
            backgroundAnimationTime.setValue(BUFFER_DATA[key]["background"]["animationSettings"]["time"])
            backgroundAnimationPositionX.setValue(BUFFER_DATA[key]["background"]["animationSettings"]["position"]["x"])
            backgroundAnimationPositionY.setValue(BUFFER_DATA[key]["background"]["animationSettings"]["position"]["y"])
            backgroundAnimationScaleX.setValue(BUFFER_DATA[key]["background"]["animationSettings"]["scale"]["x"])
            backgroundAnimationScaleY.setValue(BUFFER_DATA[key]["background"]["animationSettings"]["scale"]["y"])

        self.animationSwitch(backgroundAnimationCheckbox, backgroundAnimationTime, backgroundAnimationPositionX, backgroundAnimationPositionY, backgroundAnimationScaleX, backgroundAnimationScaleY, "background", key, None)

        backgroundAnimationCheckbox.clicked.connect(lambda: self.animationSwitch(backgroundAnimationCheckbox, backgroundAnimationTime, backgroundAnimationPositionX, backgroundAnimationPositionY, backgroundAnimationScaleX, backgroundAnimationScaleY, "background", key, None))

        formLayout.addRow(self.createLine())

        formLayout.addRow(QLabel("Text"))

        textCharaNameLayout = QHBoxLayout()
        textCharaNameLabel = QLabel("Character")
        textCharaNameLabel.setStyleSheet("padding-left: 20px;")
        textCharaNameCombobox = QComboBox()

        charaList = ['select chara', 'Макиширо Ямагаки', 'Рина Микура', 'Саймон Мацуда', 'Рэйчел Асамая', 'Мишель Мурамаки',
                     'Сэмми Коуда', 'Мичио Хаякава', 'Сегикадзе Харада', 'Дайчиро Катаяма', 'Цукико Аска',
                     'Амайя Накагава', "Румико Сакаи", 'Крис Лайтер', 'Янн Ёсимура', 'Тору Ёкояма', 'Катсураги Танабэ',
                     'Монораку', 'advanced']
        
        textCharaNameCombobox.addItems(charaList)

        textCharaNameLayout.addWidget(textCharaNameLabel)
        textCharaNameLayout.addWidget(textCharaNameCombobox)

        formLayout.addRow(textCharaNameLayout)

        textCharaNameCombobox.setStyleSheet("""
            QComboBox QAbstractItemView {
                color: rgb(85, 170, 255);	
                background-color: #373e4e;
                padding: 10px;
                selection-background-color: white;
            }
            """)
        
        if BUFFER_DATA[key]['text']['charaName'] != '':
            try:
                index = charaList.index(BUFFER_DATA[key]['text']['charaName'])
                if index == 18:
                    textCharaNameCombobox.setCurrentIndex(index)
                    self.lineEdit('',formLayout, key) 
                else:
                    textCharaNameCombobox.setCurrentIndex(index)
            except:
                index = 18
                textCharaNameCombobox.setCurrentIndex(index)
                self.lineEdit(BUFFER_DATA[key]['text']['charaName'],formLayout, key)    
        elif BUFFER_DATA[key]['text']['charaName'] == '':
            index = 0
            textCharaNameCombobox.setCurrentIndex(index)
        
        textCharaNameCombobox.currentIndexChanged.connect(lambda: self.charaTextName(textCharaNameCombobox,key,path))

        textTextLayout = QHBoxLayout()
        textTextLabel = QLabel("Text")
        textTextLabel.setStyleSheet("padding-left: 20px;")
        textTextTextEdit = QTextEdit()

        textTextLayout.addWidget(textTextLabel)
        textTextLayout.addWidget(textTextTextEdit)

        formLayout.addRow(textTextLayout)

        textTextTextEdit.setMaximumSize(500, 100)
        if BUFFER_DATA[key]['text']['text'] != '':
            textTextTextEdit.setText(BUFFER_DATA[key]['text']['text'])

        textTextTextEdit.textChanged.connect(lambda: self.saveText(textTextTextEdit.toPlainText(), key))

        formLayout.addRow(self.createLine())

        formLayout.addRow(QLabel("UI"))

        uiTimeOfDayLayout = QHBoxLayout()
        uiTimeOfDayLabel = QLabel("Time of day")
        uiTimeOfDayLabel.setStyleSheet("padding-left: 20px;")
        uiTimeOfDayCombobox = QComboBox()

        uiTimeOfDayLayout.addWidget(uiTimeOfDayLabel)
        uiTimeOfDayLayout.addWidget(uiTimeOfDayCombobox)

        formLayout.addRow(uiTimeOfDayLayout)

        timeList = ["select", "Morning", "Afternoon", "Evening", "Night"]

        uiTimeOfDayCombobox.addItems(timeList)

        if BUFFER_DATA[key]['ui']['time'] != '':
            try:
                index = timeList.index(BUFFER_DATA[key]['ui']['time'])
                uiTimeOfDayCombobox.setCurrentIndex(index)
            except:
                BUFFER_DATA[key]['ui']['time'] = ''
                uiTimeOfDayCombobox.setCurrentIndex(0)
        else:
            uiTimeOfDayCombobox.setCurrentIndex(0)

        uiTimeOfDayCombobox.currentIndexChanged.connect(lambda: self.timeOfDaySave(uiTimeOfDayCombobox, key))

        uiChapterLayout = QHBoxLayout()
        uiChapterLabel = QLabel("Chapter")
        uiChapterLabel.setStyleSheet("padding-left: 20px;")
        uiChapterLineEdit = QLineEdit()

        uiChapterLayout.addWidget(uiChapterLabel)
        uiChapterLayout.addWidget(uiChapterLineEdit)

        formLayout.addRow(uiChapterLayout)

        if BUFFER_DATA[key]['ui']['chapter'] == '':
            try:
                BUFFER_DATA[key]['ui']['chapter'] = BUFFER_DATA[str(int(key) - 1)]['ui']['chapter']
                uiChapterLineEdit.setText(BUFFER_DATA[str(int(key) - 1)]['ui']['chapter'])
            except:
                BUFFER_DATA[key]['ui']['chapter'] = ''
                uiChapterLineEdit.setText('')
        else:
            uiChapterLineEdit.setText(BUFFER_DATA[key]['ui']['chapter'])

        uiChapterLineEdit.textChanged.connect(lambda: self.saveChapter(uiChapterLineEdit.text,key))

        uiCharaEmotionLayout = QHBoxLayout()
        uiCharaEmotionLabel = QLabel('Chara emotion')
        uiCharaEmotionLabel.setStyleSheet("padding-left: 20px;")
        uiCharaEmotionButton = QPushButton("select")

        uiCharaEmotionLayout.addWidget(uiCharaEmotionLabel)
        uiCharaEmotionLayout.addWidget(uiCharaEmotionButton)

        formLayout.addRow(uiCharaEmotionLayout)

        uiCharaEmotionButton.clicked.connect(self.openHeroEmotionWindow)
 
        if BUFFER_DATA[key]['ui']['charaEmotion'] == '':
            uiCharaEmotionButton.setText('select')
        else:
            uiCharaEmotionText = BUFFER_DATA[key]['ui']['charaEmotion']
            uiCharaEmotionText = uiCharaEmotionText.replace("sprites/makishiro/", "")
            uiCharaEmotionText = uiCharaEmotionText.replace(".png", "")
            uiCharaEmotionButton.setText(uiCharaEmotionText)

        formLayout.addRow(self.createLine())

        formLayout.addRow(QLabel("Sprites"))

        spritesListWidgetLayout = QHBoxLayout()
        spritesListWidgetLabel = QLabel("Sprites hierarchy")
        spritesListWidgetLabel.setStyleSheet("padding-left: 20px;")
        self.spritesListWidget = QListWidget()

        spritesListWidgetLayout.addWidget(spritesListWidgetLabel)
        spritesListWidgetLayout.addWidget(self.spritesListWidget)

        formLayout.addRow(spritesListWidgetLayout)

        self.spritesListWidget.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.spriteList = []
        spriteListCount = int(BUFFER_DATA[key]['sprite']['count'])

        if spriteListCount > 0:
            for i in range(0, spriteListCount):
                if BUFFER_DATA[key]['sprite'][str(i)]['spriteId'] != '':
                    item = QListWidgetItem(BUFFER_DATA[key]['sprite'][str(i)]['spriteId'])
                else:
                    item = QListWidgetItem(f'Sprite: {i}')
                    BUFFER_DATA[key]['sprite'][str(i)]['spriteId'] = f'Sprite: {i}'

                self.spriteList.append(i)
                self.spritesListWidget.addItem(item)

        self.spritesListWidget.model().rowsMoved.connect(lambda: self.changeSpriteList(key))

        spritesSelectLayout = QHBoxLayout()
        spritesSelectLabel = QLabel("Select sprite")
        spritesSelectLabel.setStyleSheet("padding-left: 20px;")
        spritesSelectButton = QPushButton("select")

        spritesSelectLayout.addWidget(spritesSelectLabel)
        spritesSelectLayout.addWidget(spritesSelectButton)

        formLayout.addRow(spritesSelectLayout)

        spritesSelectButton.setEnabled(False)

        spritesSelectButton.clicked.connect(lambda: self.openSpriteWindow(key, self.id))


        spritesPositionLayout = QHBoxLayout()
        spritesPositionLabel = QLabel('Position')
        spritesPositionLabel.setStyleSheet("padding-left: 20px;")
        spritesPositionXSpinbox = QSpinBox()
        spritesPositionYSpinbox = QSpinBox()
        spritesPositionLayout.addWidget(spritesPositionLabel)
        spritesPositionLayout.addWidget(QLabel("X"))
        spritesPositionLayout.addWidget(spritesPositionXSpinbox)
        spritesPositionLayout.addWidget(QLabel("Y")) 
        spritesPositionLayout.addWidget(spritesPositionYSpinbox)

        formLayout.addRow(spritesPositionLayout)

        spritesPositionXSpinbox.setRange(-10000,10000)
        spritesPositionYSpinbox.setRange(-10000,10000)
        spritesPositionXSpinbox.setEnabled(False)
        spritesPositionYSpinbox.setEnabled(False)

        
        spritesScaleLayout = QHBoxLayout()
        spritesScaleLabel = QLabel("Scale")
        spritesScaleLabel.setStyleSheet("padding-left: 20px;")
        spritesScaleXSpinbox = QDoubleSpinBox()
        spritesScaleYSpinbox = QDoubleSpinBox()
        spritesScaleLayout.addWidget(spritesScaleLabel)
        spritesScaleLayout.addWidget(QLabel("X"))
        spritesScaleLayout.addWidget(spritesScaleXSpinbox)
        spritesScaleLayout.addWidget(QLabel("Y"))
        spritesScaleLayout.addWidget(spritesScaleYSpinbox)

        formLayout.addRow(spritesScaleLayout)

        spritesScaleXSpinbox.setRange(-10000, 10000)
        spritesScaleYSpinbox.setRange(-10000, 10000)
        spritesScaleXSpinbox.setEnabled(False)
        spritesScaleYSpinbox.setEnabled(False)


        spritesAnimationLayout = QHBoxLayout()
        spritesAnimationLaybel = QLabel("Animation")
        spritesAnimationLaybel.setStyleSheet("padding-left: 20px;")
        spritesAnimationCheckbox = QCheckBox()
        spritesAnimationLayout.addWidget(spritesAnimationLaybel)
        spritesAnimationLayout.addWidget(spritesAnimationCheckbox)

        formLayout.addRow(spritesAnimationLayout)

        spritesAnimationCheckbox.setEnabled(False)


        spritesAnimationTimeLayout = QHBoxLayout()
        spritesAnimationTimeLabel = QLabel("Animation time")
        spritesAnimationTimeLabel.setStyleSheet("padding-left: 20px;")
        spritesAnimationTimeSpinbox = QSpinBox()
        spritesAnimationTimeLayout.addWidget(spritesAnimationTimeLabel)
        spritesAnimationTimeLayout.addWidget(spritesAnimationTimeSpinbox)

        formLayout.addRow(spritesAnimationTimeLayout)

        spritesAnimationTimeSpinbox.setToolTip("in 1 sec 60 units")
        spritesAnimationTimeSpinbox.setEnabled(False)


        spritesAnimationPositionLayout = QHBoxLayout()
        spritesAnimationPositionLabel = QLabel("Position")
        spritesAnimationPositionLabel.setStyleSheet("padding-left: 20px;")
        spritesAnimationPositionXSpinbox = QSpinBox()
        spritesAnimationPositionYSpinbox = QSpinBox()
        spritesAnimationPositionLayout.addWidget(spritesAnimationPositionLabel)
        spritesAnimationPositionLayout.addWidget(QLabel("X"))
        spritesAnimationPositionLayout.addWidget(spritesAnimationPositionXSpinbox)
        spritesAnimationPositionLayout.addWidget(QLabel("Y"))
        spritesAnimationPositionLayout.addWidget(spritesAnimationPositionYSpinbox)

        formLayout.addRow(spritesAnimationPositionLayout)

        spritesAnimationPositionXSpinbox.setRange(-10000, 10000)
        spritesAnimationPositionYSpinbox.setRange(-10000, 10000)
        spritesAnimationPositionXSpinbox.setEnabled(False)
        spritesAnimationPositionYSpinbox.setEnabled(False)


        spritesAnimationScaleLayout = QHBoxLayout()
        spritesAnimationScaleLabel = QLabel("Scale")
        spritesAnimationScaleLabel.setStyleSheet("padding-left: 20px;")
        spritesAnimationScaleXSpinbox = QDoubleSpinBox()
        spritesAnimationScaleYSpinbox = QDoubleSpinBox()
        spritesAnimationScaleLayout.addWidget(spritesAnimationScaleLabel)
        spritesAnimationScaleLayout.addWidget(QLabel("X"))
        spritesAnimationScaleLayout.addWidget(spritesAnimationScaleXSpinbox)
        spritesAnimationScaleLayout.addWidget(QLabel("Y"))
        spritesAnimationScaleLayout.addWidget(spritesAnimationScaleYSpinbox)

        formLayout.addRow(spritesAnimationScaleLayout)

        spritesAnimationScaleXSpinbox.setRange(-10000, 10000)
        spritesAnimationScaleYSpinbox.setRange(-10000, 10000)
        spritesAnimationScaleXSpinbox.setEnabled(False)
        spritesAnimationScaleYSpinbox.setEnabled(False)







        spritesPositionXSpinbox.valueChanged.connect(lambda: self.saveSpinValue(spritesPositionXSpinbox, key, False, "position", "x", "sprite", str(self.id)))
        spritesPositionYSpinbox.valueChanged.connect(lambda: self.saveSpinValue(spritesPositionYSpinbox, key, False, "position", "y", "sprite", str(self.id)))

        spritesScaleXSpinbox.valueChanged.connect(lambda: self.saveSpinValue(spritesScaleXSpinbox, key, False, "scale", "x", "sprite", str(self.id)))
        spritesScaleYSpinbox.valueChanged.connect(lambda: self.saveSpinValue(spritesScaleYSpinbox, key, False, "scale", "y", "sprite", str(self.id)))

        spritesAnimationCheckbox.toggled.connect(lambda: self.spritesAnimationCheckboxClicked(spritesAnimationCheckbox, spritesAnimationTimeSpinbox, spritesAnimationPositionXSpinbox, spritesAnimationPositionYSpinbox, spritesAnimationScaleXSpinbox, spritesAnimationScaleYSpinbox))


        self.spritesListWidget.itemClicked.connect(lambda item: self.spriteSettings(item, key, spritesSelectButton, spritesPositionXSpinbox, 
                                                                                    spritesPositionYSpinbox, spritesScaleXSpinbox, spritesScaleYSpinbox,
                                                                                    spritesAnimationCheckbox, spritesAnimationTimeSpinbox, spritesAnimationPositionXSpinbox,
                                                                                    spritesAnimationPositionYSpinbox, spritesAnimationScaleXSpinbox, spritesAnimationScaleYSpinbox))


    def spritesAnimationCheckboxClicked(self, spritesAnimationCheckbox, spritesAnimationTimeSpinbox, 
                                        spritesAnimationPositionXSpinbox, spritesAnimationPositionYSpinbox, 
                                        spritesAnimationScaleXSpinbox, spritesAnimationScaleYSpinbox):
        sprite_data = BUFFER_DATA[self.key]["sprite"][str(self.id)]
        sprite_data["animation"] = spritesAnimationCheckbox.isChecked()
        
        if sprite_data["animation"] == False:
            if "animationSettings" in sprite_data:
                del sprite_data["animationSettings"]
        else:
            if "animationSettings" not in sprite_data:
                sprite_data["animationSettings"] = {
                    "time": 0,
                    "position": {"x": 0, "y": 0},
                    "scale": {"x": 1, "y": 1}
                }
        
        # Передаем sprite_data в animationSpriteSettings
        self.animationSpriteSettings(spritesAnimationCheckbox, spritesAnimationTimeSpinbox, 
                                    spritesAnimationPositionXSpinbox, spritesAnimationPositionYSpinbox, 
                                    spritesAnimationScaleXSpinbox, spritesAnimationScaleYSpinbox, 
                                    sprite_data)


    def spriteSettings(self, item, key, spritesSelectButton, spritesPositionXSpinbox, spritesPositionYSpinbox, 
                    spritesScaleXSpinbox, spritesScaleYSpinbox, spritesAnimationCheckbox, 
                    spritesAnimationTimeSpinbox, spritesAnimationPositionXSpinbox, 
                    spritesAnimationPositionYSpinbox, spritesAnimationScaleXSpinbox, 
                    spritesAnimationScaleYSpinbox):
        itemText = item.text()
        self.id = None

        # Найти индекс текущего спрайта
        for i in range(BUFFER_DATA[key]["sprite"]["count"]):
            if itemText == BUFFER_DATA[key]["sprite"][str(i)]["spriteId"]:
                self.id = i

        # Проверить наличие настроек анимации и других параметров для этого спрайта
        sprite_data = BUFFER_DATA[key]["sprite"][str(self.id)]
        
        if "animationSettings" not in sprite_data:
            # Если настройки анимации отсутствуют, инициализируем их
            sprite_data["animationSettings"] = {
                "time": 0,
                "position": {"x": 0, "y": 0},
                "scale": {"x": 1.0, "y": 1.0}
            }

        # Обновление интерфейса с использованием данных спрайта
        spritesSelectButton.setEnabled(True)
        spritesSelectButtonText = sprite_data["name"]
        spritesSelectButtonText = spritesSelectButtonText[spritesSelectButtonText.find("/", spritesSelectButtonText.find("/") + 1) + 1:].strip()
        spritesSelectButton.setText(spritesSelectButtonText)

        spritesPositionXSpinbox.setEnabled(True)
        spritesPositionYSpinbox.setEnabled(True)
        spritesPositionXSpinbox.setValue(sprite_data["position"]["x"])
        spritesPositionYSpinbox.setValue(sprite_data["position"]["y"])

        spritesScaleXSpinbox.setEnabled(True)
        spritesScaleYSpinbox.setEnabled(True)
        spritesScaleXSpinbox.setValue(sprite_data["scale"]["x"])
        spritesScaleYSpinbox.setValue(sprite_data["scale"]["y"])

        # Настройки анимации
        self.animationSpriteSettings(spritesAnimationCheckbox, spritesAnimationTimeSpinbox, 
                                    spritesAnimationPositionXSpinbox, spritesAnimationPositionYSpinbox, 
                                    spritesAnimationScaleXSpinbox, spritesAnimationScaleYSpinbox, 
                                    sprite_data)

    def animationSpriteSettings(self, spritesAnimationCheckbox, spritesAnimationTimeSpinbox, 
                                spritesAnimationPositionXSpinbox, spritesAnimationPositionYSpinbox, 
                                spritesAnimationScaleXSpinbox, spritesAnimationScaleYSpinbox, 
                                sprite_data):
        
        # Активация чекбокса анимации
        spritesAnimationCheckbox.setEnabled(True)
        
        # Проверка состояния анимации
        if sprite_data["animation"] == False:
            # Если анимация отключена, отключаем поля и обнуляем значения
            spritesAnimationTimeSpinbox.setEnabled(False)
            spritesAnimationPositionXSpinbox.setEnabled(False)
            spritesAnimationPositionYSpinbox.setEnabled(False)
            spritesAnimationScaleXSpinbox.setEnabled(False)
            spritesAnimationScaleYSpinbox.setEnabled(False)

            spritesAnimationCheckbox.setChecked(False)
            spritesAnimationTimeSpinbox.setValue(0)
            spritesAnimationPositionXSpinbox.setValue(0)
            spritesAnimationPositionYSpinbox.setValue(0)
            spritesAnimationScaleXSpinbox.setValue(0)
            spritesAnimationScaleYSpinbox.setValue(0)
        else:
            # Если анимация включена, включаем поля и устанавливаем значения из данных
            spritesAnimationTimeSpinbox.setEnabled(True)
            spritesAnimationPositionXSpinbox.setEnabled(True)
            spritesAnimationPositionYSpinbox.setEnabled(True)
            spritesAnimationScaleXSpinbox.setEnabled(True)
            spritesAnimationScaleYSpinbox.setEnabled(True)

            spritesAnimationCheckbox.setChecked(True)
            spritesAnimationTimeSpinbox.setValue(sprite_data["animationSettings"]["time"])
            spritesAnimationPositionXSpinbox.setValue(sprite_data["animationSettings"]["position"]["x"])
            spritesAnimationPositionYSpinbox.setValue(sprite_data["animationSettings"]["position"]["y"])
            spritesAnimationScaleXSpinbox.setValue(sprite_data["animationSettings"]["scale"]["x"])
            spritesAnimationScaleYSpinbox.setValue(sprite_data["animationSettings"]["scale"]["y"])


    def animationSwitch(self, checkbox, time, positionX, positionY, scaleX, scaleY, type, key, index):
        condition = checkbox.isChecked()
        time.setEnabled(condition)
        positionX.setEnabled(condition)
        positionY.setEnabled(condition)
        scaleX.setEnabled(condition)
        scaleY.setEnabled(condition)
        if condition == True:
            if type == "background":
                BUFFER_DATA[key][type]["animation"] = True
                if 'animationSettings' not in BUFFER_DATA[key][type]:
                    BUFFER_DATA[key][type]['animationSettings'] = {
                        "time": 0,
                        "position": {
                            "x": 0,
                            "y": 0
                        },
                        "scale": {
                            "x": 1.0,
                            "y": 1.0
                        }
                    }
                self.blockSignalsForAnimation(time, positionX, positionY, scaleX, scaleY, BUFFER_DATA[key]["background"]["animationSettings"])
            elif type == "sprite":
                BUFFER_DATA[key][type][index]["animation"] = True
                if 'animationSettings' not in BUFFER_DATA[key][type][index]:
                    BUFFER_DATA[key][type][index]['animationSettings'] = {
                        "time": 0,
                        "position": {
                            "x": 0,
                            "y": 0
                        },
                        "scale": {
                            "x": 1.0,
                            "y": 1.0
                        }
                    }
                self.blockSignalsForAnimation(time, positionX, positionY, scaleX, scaleY, BUFFER_DATA[key]["sprite"][index]["animationSettings"])
        else:
            if type == "background":
                BUFFER_DATA[key][type]["animation"] = False
                if 'animationSettings' in BUFFER_DATA[key][type]:
                    del BUFFER_DATA[key][type]['animationSettings']
                self.blockSignalsForAnimation(time, positionX, positionY, scaleX, scaleY, None)
            elif type == "sprite":
                BUFFER_DATA[key][type][index]["animation"] = False
                if 'animationSettings' in BUFFER_DATA[key][type][index]:
                    del BUFFER_DATA[key][type][index]['animationSettings']
                self.blockSignalsForAnimation(time, positionX, positionY, scaleX, scaleY, None)

    def createLine(self):
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        return line

    def saveSpinValue(self, spinbox, key, animation, type, item, object, index):
        if animation == False:
            if object == "background":
                BUFFER_DATA[key][object][type][item] = spinbox.value()
            elif object == "sprite":
                BUFFER_DATA[key][object][index][type][item] = spinbox.value()
        else:
            if object == "background" and type != "time":
                BUFFER_DATA[key][object]["animationSettings"][type][item] = spinbox.value()
            elif object == "sprite" and type != "time":
                BUFFER_DATA[key][object][index]["animationSettings"][type][item] = spinbox.value()
            elif object == "background" and type == "time":
                BUFFER_DATA[key][object]["animationSettings"][type] = spinbox.value()
            elif object == "sprite" and type == "time":
                BUFFER_DATA[key][object][index]["animationSettings"][type] = spinbox.value()
            
    def blockSignalsForAnimation(self, time, positionX, positionY, scaleX, scaleY, animationSettings):
        time.blockSignals(True)
        positionX.blockSignals(True)
        positionY.blockSignals(True)
        scaleX.blockSignals(True)
        scaleY.blockSignals(True)

        if animationSettings:
            time.setValue(animationSettings["time"])
            positionX.setValue(animationSettings["position"]["x"])
            positionY.setValue(animationSettings["position"]["y"])
            scaleX.setValue(animationSettings["scale"]["x"])
            scaleY.setValue(animationSettings["scale"]["y"])
        else:
            time.setValue(0)
            positionX.setValue(0)
            positionY.setValue(0)
            scaleX.setValue(0)
            scaleY.setValue(0)

        time.blockSignals(False)
        positionX.blockSignals(False)
        positionY.blockSignals(False)
        scaleX.blockSignals(False)
        scaleY.blockSignals(False)
                

    def onSpriteSelect(self, selectedImage):
        key = self.path[0] if hasattr(self, 'path') and self.path else None
        BUFFER_DATA[key]['sprite'][self.index]['name'] = selectedImage
        self.spriteSelectButton.setText(selectedImage)
        self.layoutChecker(self.formLayout, self.key, self.item)

    def layoutChecker(self, layout, key, item):
        try:
            self.spriteLayout.deleteLater()
            self.sptiteSettings(item, key, layout)
        except:
            self.sptiteSettings(item, key, layout)
        layout.addRow(self.spriteLayout)

    def saveSpritelist(self, key):
        sprite_order = [self.spritesListWidget.item(i).text() for i in range(self.spritesListWidget.count())]
        sprite_count = int(BUFFER_DATA[key]['sprite']['count'])
        buffer = BUFFER_DATA[key]['sprite']
        updated_sprites = {'count': sprite_count}

        original_indices = {buffer[str(i)]['spriteId']: i for i in range(sprite_count)}

        for new_index, object_name in enumerate(sprite_order):
            original_index = original_indices[object_name]
            updated_sprites[str(new_index)] = buffer[str(original_index)]

        BUFFER_DATA[key]['sprite'] = updated_sprites
        self.inspectorLoad(self.path)

    def changeSpriteList(self, key):
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

    def lineEditSave(self, text, key):
        BUFFER_DATA[key]['text']['charaName'] = text

    def lineEdit(self, text, layout, key):
        textLayout = QHBoxLayout()
        textName = QLabel("advanced name")
        textLineEdit = QLineEdit(text)

        textName.setStyleSheet("padding-left: 20px;")

        textLayout.addWidget(textName)
        textLayout.addWidget(textLineEdit)

        layout.addRow(textLayout)
        textLineEdit.textChanged.connect(lambda: self.lineEditSave(textLineEdit.text(), key))

    def charaTextName(self,qbox,key,path):
        text = qbox.currentText()
        BUFFER_DATA[key]['text']['charaName'] = text
        self.inspectorLoad(path)

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
