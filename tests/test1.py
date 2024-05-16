import sys
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFormLayout, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QRadioButton, QSlider, QDateEdit, QTimeEdit, QDateTimeEdit, QPushButton

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

        # Примеры различных виджетов
        line_edit = QLineEdit()
        text_edit = QTextEdit()
        spin_box = QSpinBox()
        double_spin_box = QDoubleSpinBox()
        combo_box = QComboBox()
        combo_box.addItems(["Option 1", "Option 2", "Option 3"])
        check_box = QCheckBox("Check me")
        radio_button = QRadioButton("Select me")
        slider = QSlider()
        date_edit = QDateEdit()
        time_edit = QTimeEdit()
        date_time_edit = QDateTimeEdit()

        # Добавляем виджеты в форму
        form_layout.addRow("QLineEdit", line_edit)
        form_layout.addRow("QTextEdit", text_edit)
        form_layout.addRow("QSpinBox", spin_box)
        form_layout.addRow("QDoubleSpinBox", double_spin_box)
        form_layout.addRow("QComboBox", combo_box)
        form_layout.addRow("QCheckBox", check_box)
        form_layout.addRow("QRadioButton", radio_button)
        form_layout.addRow("QSlider", slider)
        form_layout.addRow("QDateEdit", date_edit)
        form_layout.addRow("QTimeEdit", time_edit)
        form_layout.addRow("QDateTimeEdit", date_time_edit)

        # Добавляем форму в основной макет
        main_layout.addLayout(form_layout)

        # Кнопка для вывода значений характеристик
        self.show_values_button = QPushButton('Показать значения')
        self.show_values_button.clicked.connect(self.show_values)
        main_layout.addWidget(self.show_values_button)

        # Устанавливаем основной макет в окно
        self.setLayout(main_layout)

    def show_values(self):
        # Считываем значения из полей и выводим их в консоль (пример)
        pass

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = CharacteristicEditor()
    editor.show()
    sys.exit(app.exec())
