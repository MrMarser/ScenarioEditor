from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QFormLayout, QLabel, QSpinBox, QHBoxLayout, QVBoxLayout
import sys
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QFormLayout Example")
        self.setGeometry(100, 100, 400, 300)

        container = QWidget()
        self.setCentralWidget(container)

        formLayout = QFormLayout()

        # Создаем два QSpinBox
        spinBox1 = QSpinBox()
        spinBox2 = QSpinBox()

        # Устанавливаем значения по умолчанию, минимальные и максимальные значения
        spinBox1.setRange(0, 100)
        spinBox1.setValue(50)
        spinBox2.setRange(0, 100)
        spinBox2.setValue(25)

        # Создаем горизонтальный макет для размещения двух QSpinBox и их меток
        hboxLayout = QHBoxLayout()
        
        # Добавляем первую метку и первый QSpinBox
        hboxLayout.addWidget(QLabel("SpinBox 1:"))
        hboxLayout.addWidget(spinBox1)
        
        # Добавляем вторую метку и второй QSpinBox
        hboxLayout.addWidget(QLabel("SpinBox 2:"))
        hboxLayout.addWidget(spinBox2)

        # Создаем виджет контейнера для горизонтального макета
        containerWidget = QWidget()
        containerWidget.setLayout(hboxLayout)

        # Добавляем горизонтальный макет (через контейнер) в QFormLayout
        formLayout.addRow(QLabel("SpinBoxes:"), containerWidget)

        container.setLayout(formLayout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
