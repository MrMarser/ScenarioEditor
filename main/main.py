import sys
import os
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QDockWidget, QTreeWidget, QTreeWidgetItem, QFileDialog, QToolBar, QMenu, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QMessageBox
from PyQt6.QtGui import QAction, QIcon, QWheelEvent, QPainter, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scenario Editor")
        self.setGeometry(0, 0, 1920, 1080)
        self.showMaximized()

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
                with open(fileName, "r") as file:
                    content = json.load(file)
                    self.updateTreeWidget(content)
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

    def updateTreeWidget(self, data):
        if not hasattr(self, 'tree_widget'):
            self.tree_widget = QTreeWidget()

            self.tree_widget.setHeaderLabels(['Scene Elements'])

            self.tree_widget.header().setStyleSheet("""
            QHeaderView::section {
                background-color: rgb(50, 70, 90); 
                color: white; 
                font-size: 14px; 
            }
        """)

            dock_widget = QDockWidget("", self)
            dock_widget.setStyleSheet("background-color: rgb(30, 40, 50)")
            dock_widget.setWidget(self.tree_widget)
            self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, dock_widget)
        else:
            self.tree_widget.clear()
        self.tree_widget.setStyleSheet("""
            background-color: rgb(50, 70, 90);
            color: white;
        """)
        self.load_tree_items(data, self.tree_widget)

    def load_tree_items(self, data, parent_item):
        if isinstance(data, dict):
            for key, value in data.items():
                child_item = QTreeWidgetItem(parent_item, [str(key)])
                self.load_tree_items(value, child_item)
        elif isinstance(data, list):
            for index, item in enumerate(data):
                child_item = QTreeWidgetItem(parent_item, [f'Item {index}'])
                self.load_tree_items(item, child_item)
        else:
            QTreeWidgetItem(parent_item, [str(data)])

app = QApplication(sys.argv)
window = MainWindow()
window.barMenu()
window.TollBar()
window.createCanvas()
window.show()

app.setStyleSheet(Path("main/style.css").read_text())
sys.exit(app.exec())
