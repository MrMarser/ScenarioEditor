import sys
import json
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer, QPointF, QRectF
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QColor, QWheelEvent, QTransform

# Пример JSON данных
json_data = '''
{
    "images": [
        {
            "path": "tests/Neferpitou.jpg",
            "x": 400,
            "y": 400,
            "scale_x": 1.0,
            "scale_y": 1.0,
            "target_x": 800,
            "target_y": 600,
            "target_scale_x": 0.5,
            "animation_duration": 1000
        },
        {
            "path": "tests/Amaya_acrid1.png",
            "x": 0,
            "y": 0,
            "scale_x": 0.8,
            "scale_y": 0.8,
            "target_x": 0,
            "target_y": 0,
            "target_scale_x": 4,
            "animation_duration": 2000
        }
    ]
}
'''

# Главный виджет
class ImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Canvas with PNG Images")
        self.setGeometry(100, 100, 1600, 900)
        
        self.animation_active = False  # Флаг для отслеживания состояния анимации

        # Чтение JSON данных
        self.image_data = json.loads(json_data)

        # Создаем сцену и вид
        self.scene = QGraphicsScene(0, 0, 1600, 900)
        self.view = ZoomableGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, 1600, 900)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Установка серого фона
        self.view.setBackgroundBrush(QBrush(QColor(169, 169, 169)))  # серый фон

        # Создаем белую область 1600x900
        white_background = self.scene.addRect(QRectF(0, 0, 1600, 900), brush=QBrush(QColor(255, 255, 255)))  # белый фон

        # Добавляем изображения на сцену
        self.image_items = []
        self.load_images()  # Загружаем изображения на сцену

        # Кнопка для запуска/остановки анимации
        self.button_start_animation = QPushButton("Start Animation", self)
        self.button_start_animation.clicked.connect(self.toggle_animation)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.button_start_animation)
        self.setLayout(layout)

    def load_images(self):
        """Загружает изображения на сцену."""
        self.image_items = []  # Очищаем старые элементы
        for image_info in self.image_data["images"]:
            pixmap = QPixmap(image_info["path"])
            if pixmap.isNull():
                print(f"Failed to load image: {image_info['path']}")
                continue
            item = QGraphicsPixmapItem(pixmap)
            item.setPos(image_info["x"], image_info["y"])
            item.setScale(image_info["scale_x"])
            self.scene.addItem(item)
            self.image_items.append((item, image_info))  # сохраняем item и его параметры

    def toggle_animation(self):
        if not self.animation_active:
            self.start_animation()
            self.button_start_animation.setText("Stop Animation")
        else:
            self.stop_animation()
            self.button_start_animation.setText("Start Animation")
        self.animation_active = not self.animation_active

    def start_animation(self):
        self.timers = []  # Список таймеров для каждой анимации
        for item, image_info in self.image_items:
            start_pos = item.pos()
            start_scale_x = item.transform().m11()  # Текущий масштаб по оси X
            start_scale_y = item.transform().m22()  # Текущий масштаб по оси Y

            # Берем индивидуальные цели для каждой картинки
            target_x = image_info.get("target_x", start_pos.x())
            target_y = image_info.get("target_y", start_pos.y())
            target_scale_x = image_info.get("target_scale_x", start_scale_x)
            target_scale_y = image_info.get("target_scale_y", start_scale_y)

            # Берем индивидуальное время анимации для каждого спрайта
            duration = image_info.get("animation_duration", 1000)

            timer = QTimer(self)
            start_time = 0
            interval = 16  # Примерно 60 кадров в секунду

            # Теперь мы передаем timer внутрь функции animate
            animate_function = self.create_animate_function(item, start_pos, start_scale_x, start_scale_y, target_x, target_y, target_scale_x, target_scale_y, timer, duration)
            timer.timeout.connect(animate_function)
            timer.start(interval)
            self.timers.append(timer)  # Сохраняем таймер для остановки

    def stop_animation(self):
        # Останавливаем все таймеры
        for timer in self.timers:
            timer.stop()

        # Очищаем сцену и загружаем изображения заново
        self.scene.clear()  # Очищаем всю сцену
        white_background = self.scene.addRect(QRectF(0, 0, 1600, 900), brush=QBrush(QColor(255, 255, 255)))  # Добавляем белый фон обратно
        self.load_images()  # Загружаем изображения обратно на сцену

    def create_animate_function(self, item, start_pos, start_scale_x, start_scale_y, target_x, target_y, target_scale_x, target_scale_y, timer, duration):
        interval = 16  # Примерно 60 кадров в секунду
        start_time = 0
        
        def animate():
            nonlocal start_time

            if start_time >= duration:
                timer.stop()
                return

            progress = start_time / duration

            # Перемещение
            new_x = start_pos.x() + progress * (target_x - start_pos.x())
            new_y = start_pos.y() + progress * (target_y - start_pos.y())
            item.setPos(QPointF(new_x, new_y))

            # Изменение масштаба по осям
            new_scale_x = start_scale_x + progress * (target_scale_x - start_scale_x)
            new_scale_y = start_scale_y + progress * (target_scale_y - start_scale_y)
            item.setTransform(QTransform().scale(new_scale_x, new_scale_y))

            start_time += interval

        return animate


# Класс для управления масштабированием с помощью колеса мыши
class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.scale_factor = 1.0
        self.min_scale = 0.5  # минимальный масштаб
        self.max_scale = 2.0  # максимальный масштаб

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y() / 120  # направление движения колеса
        zoom_in_factor = 1.1
        zoom_out_factor = 0.9

        if delta > 0:
            factor = zoom_in_factor
        else:
            factor = zoom_out_factor

        new_scale = self.scale_factor * factor
        if self.min_scale <= new_scale <= self.max_scale:
            self.scale(factor, factor)
            self.scale_factor = new_scale

# Запуск приложения
app = QApplication(sys.argv)
widget = ImageWidget()
widget.show()
sys.exit(app.exec())
