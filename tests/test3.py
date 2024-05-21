from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QListWidgetItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QMessageBox
from PyQt6.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Layer List Example")
        self.setGeometry(100, 100, 400, 300)

        container = QWidget()
        self.setCentralWidget(container)

        self.layout = QVBoxLayout()

        # Создаем QListWidget с поддержкой перетаскивания
        self.listWidget = QListWidget()
        self.listWidget.setDragDropMode(QListWidget.DragDropMode.InternalMove)

        # Добавляем кнопки для управления элементами
        self.addButton = QPushButton("Add Layer")
        self.deleteButton = QPushButton("Delete Selected Layer")

        self.addButton.clicked.connect(self.addLayer)
        self.deleteButton.clicked.connect(self.deleteLayer)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.deleteButton)

        self.layout.addWidget(self.listWidget)
        self.layout.addLayout(buttonLayout)
        container.setLayout(self.layout)

    def addLayer(self):
        # Добавляем новый слой
        count = self.listWidget.count() + 1
        item = QListWidgetItem(f"Layer {count}")
        self.listWidget.addItem(item)

    def deleteLayer(self):
        # Удаляем выбранный слой
        selected_items = self.listWidget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select a layer to delete")
            return

        for item in selected_items:
            self.listWidget.takeItem(self.listWidget.row(item))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
