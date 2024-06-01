import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QListWidget Click Example")

        self.spritesListWidget = QListWidget()
        self.spritesListWidget.addItems(["Sprite 1", "Sprite 2", "Sprite 3"])

        layout = QVBoxLayout()
        layout.addWidget(self.spritesListWidget)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

        # Подключение сигнала itemClicked к лямбда-выражению, которое печатает True
        self.spritesListWidget.itemClicked.connect(lambda item: print(f"Clicked on: {item.text()}"))

        # Программное выделение элемента и имитация клика
        self.select_item(1)

    def select_item(self, index):
        item = self.spritesListWidget.item(index)
        self.spritesListWidget.setCurrentItem(item)
        # Имитация сигнала клика
        self.spritesListWidget.itemClicked.emit(item)

app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()

