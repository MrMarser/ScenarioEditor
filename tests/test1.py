import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QFormLayout, QPushButton

class CharacteristicEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Устанавливаем заголовок окна
        self.setWindowTitle('Редактор характеристик')

        # Создаем основной вертикальный макет
        main_layout = QVBoxLayout()

        # Создаем форму для характеристик
        form_layout = QFormLayout()

        # Список характеристик
        self.characteristics = {
            "Высота": "",
            "Вес": "",
            "Возраст": "",
            "Цвет глаз": "",
            "Цвет волос": ""
        }

        # Поля ввода для каждой характеристики
        self.fields = {}
        for characteristic in self.characteristics:
            label = QLabel(characteristic)
            line_edit = QLineEdit()
            form_layout.addRow(label, line_edit)
            self.fields[characteristic] = line_edit

        # Добавляем форму в основной макет
        main_layout.addLayout(form_layout)

        # Кнопка для вывода значений характеристик
        self.show_values_button = QPushButton('Показать значения')
        self.show_values_button.clicked.connect(self.show_values)
        main_layout.addWidget(self.show_values_button)

        # Устанавливаем основной макет в окно
        self.setLayout(main_layout)

    def show_values(self):
        # Считываем значения из полей и выводим их в консоль
        for characteristic, line_edit in self.fields.items():
            value = line_edit.text()
            print(f"{characteristic}: {value}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = CharacteristicEditor()
    editor.show()
    sys.exit(app.exec())
