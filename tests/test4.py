from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QFormLayout, QLabel, QVBoxLayout
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt
import sys
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QFormLayout Example")
        self.setGeometry(100, 100, 400, 300)

        container = QWidget()
        self.setCentralWidget(container)

        formLayout = QFormLayout()

        # Добавляем текстовые метки
        mainLabel = QLabel("Main Section")
        formLayout.addRow(mainLabel)

        # Создаем дочерние объекты с выделением
        childLabel1 = QLabel("Child 1")
        childLabel2 = QLabel("Child 2")
        childLabel3 = QLabel("Child 3")

        # Настройка шрифта и стиля для выделения дочерних объектов
        childLabel1.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        childLabel1.setStyleSheet("padding-left: 20px; color: blue;")
        
        childLabel2.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        childLabel2.setStyleSheet("padding-left: 20px; color: blue;")
        
        childLabel3.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        childLabel3.setStyleSheet("padding-left: 20px; color: blue;")

        # Добавляем дочерние объекты в форму
        formLayout.addRow(childLabel1)
        formLayout.addRow(childLabel2)
        formLayout.addRow(childLabel3)

        container.setLayout(formLayout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
