from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget
import sys


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Layer Tree Example")
        self.setGeometry(100, 100, 400, 300)

        container = QWidget()
        self.setCentralWidget(container)

        layout = QVBoxLayout()

        # Создаем QTreeWidget с поддержкой перетаскивания
        self.treeWidget = QTreeWidget()
        self.treeWidget.setHeaderLabel("Layers")
        self.treeWidget.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)

        # Добавляем элементы в дерево
        for i in range(3):
            parent = QTreeWidgetItem(self.treeWidget, [f"Group {i + 1}"])
            for j in range(3):
                QTreeWidgetItem(parent, [f"Layer {i + 1}.{j + 1}"])

        layout.addWidget(self.treeWidget)
        container.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
