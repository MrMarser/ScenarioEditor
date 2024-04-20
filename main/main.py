import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QToolBar
from PyQt6.QtGui import QAction




class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("scenarioEditor")
        self.setGeometry(0,0,1920,1080)
        self.showMaximized()



    def barMenu(self):
        menu = self.menuBar()
        fileMenu = menu.addMenu("&File")


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
                    print(str(content)) ##TODO
            except Exception as e:
                print("error", e)
        else:
            print("error")

    def TollBar(self):
        pass


app = QApplication(sys.argv)
window = MainWindow()
window.barMenu()
window.show()

app.setStyleSheet(Path("main/style.css").read_text())
sys.exit(app.exec())
