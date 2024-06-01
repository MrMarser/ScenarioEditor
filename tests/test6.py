import sys
from PyQt6.QtWidgets import QApplication, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.itemMoved = []

    def dropEvent(self, event):
        super().dropEvent(event)
        self.logMovedItems()

    def logMovedItems(self):
        self.itemMoved = []
        for index in range(self.count()):
            item = self.item(index)
            self.itemMoved.append(item.text())
        print("Items moved to new positions:", self.itemMoved)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QListWidget Drag and Drop Example")
        self.setGeometry(100, 100, 300, 400)
        
        self.layout = QVBoxLayout()
        self.listWidget = DraggableListWidget(self)
        
        for i in range(10):
            item = QListWidgetItem(f"Item {i}")
            self.listWidget.addItem(item)
        
        self.layout.addWidget(self.listWidget)
        self.setLayout(self.layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
