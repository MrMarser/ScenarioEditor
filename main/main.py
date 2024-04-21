import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolBar, QMenu, QGraphicsView, QGraphicsScene, QGraphicsRectItem
from PyQt6.QtGui import QAction, QIcon, QWheelEvent, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("scenarioEditor")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()

    def barMenu(self):
        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")
        menu.setStyleSheet("font-size: 15px")

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
                with open(fileName, "r") as file:
                    content = file.read()
                    print(str(content))  # TODO
            except Exception as e:
                print("error", e)
        else:
            print("error")

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
        ##addSprite.triggered.connect() ##TODO
        ##newFrame.triggered.connect() ##TODO
        ##playAnimation.triggered.connect() ##TODO


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


    def folders(self):
        folders = []
        folderPath = "sprites/"
        if os.path.exists(folderPath):
            for item in os.listdir(folderPath):
                itemPath = os.path.join(folderPath, item)
                if os.path.isdir(itemPath):
                    folders.append(item)
        return folders

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




app = QApplication(sys.argv)
window = MainWindow()
window.barMenu()
window.TollBar()
window.createCanvas()
window.show()

app.setStyleSheet(Path("main/style.css").read_text())
sys.exit(app.exec())
