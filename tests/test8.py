import sys
import json
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer, QPointF, QRectF, Qt, QElapsedTimer
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QColor, QWheelEvent, QTransform, QFont,  QPolygonF, QPainterPath, QRegion

# Ваш JSON-данные остаются без изменений
json_data = '''
{
    "background": {
        "name": "backgrounds/bc1.png",
        "position": {
            "x": 0,
            "y": 0
        },
        "scale": {
            "x": 1.25,
            "y": 1.25
        },
        "animation": true,
        "animationSettings": {
            "time": 2000,
            "position": {
                "x": 1000,
                "y": 300
            },
            "scale": {
                "x": 1.25,
                "y": 1.25
            }
        }
    },
    "text": {
        "charaName": "Макиширо Ямагаки",
        "text": "vel=0,0 press=-626.106,-775.317 last=-626.106,-775.317 Δ 626.106,775.317) : no target window."
    },
    "ui": {
        "time": "Afternoon",
        "chapter": " Prologue",
        "emotion": true,
        "charaEmotion": "tests/Amaya_acrid1.png",
        "charaEmotionBackground": "tests/Neferpitou.jpg",
        "charaEmotionBackgroundPosition": {
            "x": 0,
            "y": 0
        },
        "charaEmotionBackgroundScale": {
            "x": 4.0,
            "y": 4.0
        }
    },
    "sprite": {
        "count": 3,
        "0": {
            "spriteId": "Sprite: 0",
            "name": "sprites/basic/Simon.png",
            "position": {
                "x": 0,
                "y": 300
            },
            "scale": {
                "x": 0.5,
                "y": 0.5
            },
            "animation": true,
            "animationSettings": {
                "time": 2000,
                "position": {
                    "x": 500,
                    "y": 300
                },
                "scale": {
                    "x": 0.5,
                    "y": 0.5
                }
            }
        },
        "1": {
            "spriteId": "Sprite: 2",
            "name": "sprites/basic/Simon.png",
            "position": {
                "x": 500,
                "y": 300
            },
            "scale": {
                "x": 0.5,
                "y": 0.5
            },
            "animation": true,
            "animationSettings": {
                "time": 2000,
                "position": {
                    "x": 1000,
                    "y": 300
                },
                "scale": {
                    "x": 0.5,
                    "y": 0.5
                }
            }
        },
        "2": {
            "spriteId": "Sprite: 1",
            "name": "sprites/basic/Simon.png",
            "position": {
                "x": 700,
                "y": 300
            },
            "scale": {
                "x": 0.5,
                "y": 0.5
            },
            "animation": true,
            "animationSettings": {
                "time": 2000,
                "position": {
                    "x": 1000,
                    "y": 300
                },
                "scale": {
                    "x": 0.5,
                    "y": 0.5
                }
            }
        }
    }
}
'''

class ImageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Canvas with PNG Images")
        self.setGeometry(100, 100, 1600, 900)

        self.animation_active = False

        # Чтение JSON данных
        self.image_data = json.loads(json_data)

        # Создаем сцену и вид
        self.scene = QGraphicsScene(0, 0, 1600, 900)
        self.view = ZoomableGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, 1600, 900)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Установка серого фона
        self.view.setBackgroundBrush(QBrush(QColor(169, 169, 169)))

        # Добавляем изображения на сцену
        self.image_items = []
        self.load_images()

        # Кнопка для запуска/остановки анимации
        self.button_start_animation = QPushButton("Start Animation", self)
        self.button_start_animation.clicked.connect(self.toggle_animation)

        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.button_start_animation)
        self.setLayout(layout)

    def load_images(self):
        """Загружает фон и спрайты на сцену."""
        self.scene.clear()

        white_background = self.scene.addRect(QRectF(0, 0, 1600, 900), brush=QBrush(QColor(255, 255, 255)))
        white_background.setZValue(-10)

        # Загружаем фон
        background_info = self.image_data.get("background", {})
        if background_info:
            background_pixmap = QPixmap(background_info['name'])
            if not background_pixmap.isNull():
                self.background_item = QGraphicsPixmapItem(background_pixmap)
                self.background_item.setPos(background_info["position"]["x"], background_info["position"]["y"])
                self.background_item.setTransform(QTransform().scale(background_info["scale"]["x"], background_info["scale"]["y"]))
                self.background_item.setZValue(-1)
                self.scene.addItem(self.background_item)

        sprite_data = self.image_data.get("sprite", {})
        sprite_count = sprite_data.get("count", 0)
        self.image_items = []

        for i in range(sprite_count):
            sprite_info = sprite_data.get(str(i), {})
            sprite_pixmap = QPixmap(sprite_info['name'])
            if not sprite_pixmap.isNull():
                sprite_item = QGraphicsPixmapItem(sprite_pixmap)
                sprite_item.setPos(sprite_info["position"]["x"], sprite_info["position"]["y"])
                sprite_item.setTransform(QTransform().scale(sprite_info["scale"]["x"], sprite_info["scale"]["y"]))
                sprite_item.setZValue(i)
                self.scene.addItem(sprite_item)
                self.image_items.append((sprite_item, sprite_info))

        # Создаем фиксированное изображение
        mhimage = "tests/HeroMainDialogueTheme.PNG"
        nmhimage = "tests/notNeroMainDialogueTheme.PNG"
        fixed_image_path = mhimage if self.image_data["text"]["charaName"] == "Макиширо Ямагаки" else nmhimage
        self.fixed_image = QGraphicsPixmapItem(QPixmap(fixed_image_path))
        self.fixed_image.setPos(0, 0)
        self.fixed_image.setZValue(99)
        self.scene.addItem(self.fixed_image)

        # Добавляем текстовые элементы
        self.add_text_elements()

        # Если emotion включен, добавляем charaEmotionBackground
        if self.image_data["ui"]["emotion"]:
            self.emotionWindow()

    def emotionWindow(self):
        """Создаем фон для эмоций с полигональной маской."""
        chara_emotion_background = self.image_data["ui"].get("charaEmotionBackground", None)
        if chara_emotion_background:
            emotion_bg_pixmap = QPixmap(chara_emotion_background)
            if not emotion_bg_pixmap.isNull():
                emotion_bg_pos = self.image_data["ui"].get("charaEmotionBackgroundPosition", {"x": 0, "y": 0})
                emotion_bg_scale = self.image_data["ui"].get("charaEmotionBackgroundScale", {"x": 1.0, "y": 1.0})

                # Масштабируем изображение
                scaled_pixmap = emotion_bg_pixmap.scaled(
                    int(emotion_bg_pixmap.width() * emotion_bg_scale["x"]),
                    int(emotion_bg_pixmap.height() * emotion_bg_scale["y"])
                )

                self.chara_emotion_background_item = QGraphicsPixmapItem(scaled_pixmap)
                self.chara_emotion_background_item.setPos(emotion_bg_pos["x"], emotion_bg_pos["y"])
                self.chara_emotion_background_item.setZValue(99)

                # Создаем полигон для маски
                mask_polygon = QPolygonF([QPointF(1300, 300), QPointF(1600, 400), QPointF(1600, 900), QPointF(1100, 900)])

                # Создаем QPainterPath для маски
                mask_path = QPainterPath()
                mask_path.addPolygon(mask_polygon)

                # Применяем маску через QRegion
                mask_region = QRegion(mask_path.toFillPolygon().toPolygon())
                self.chara_emotion_background_item.setPixmap(scaled_pixmap)
                self.chara_emotion_background_item.setShapeMode(QGraphicsPixmapItem.ShapeMode.MaskShape)

                # Маскируем все, что за пределами полигона
                mask_image = QPixmap(scaled_pixmap.size())
                mask_image.fill(Qt.GlobalColor.transparent)
                painter = QPainter(mask_image)
                painter.setClipRegion(mask_region)
                painter.drawPixmap(0, 0, scaled_pixmap)
                painter.end()

                self.chara_emotion_background_item.setPixmap(mask_image)
                self.scene.addItem(self.chara_emotion_background_item)

                mhimagePath = self.image_data["ui"]["charaEmotion"]
                self.mhimage = QGraphicsPixmapItem(QPixmap(mhimagePath))
                self.mhimage.setPos(1125, 400)
                self.mhimage.setZValue(99)

                self.mhimage.setTransform(QTransform().scale(0.4, 0.4))

                self.scene.addItem(self.mhimage)

    def add_text_elements(self):
        # Текстовые элементы
        text = self.image_data["text"]["text"]
        self.text_item = self.scene.addText(text)
        self.text_item.setDefaultTextColor(QColor(255, 255, 255))
        self.text_item.setPos(25, 715)
        self.text_item.setTextWidth(1100)
        self.text_item.setZValue(100)
        self.text_item.setFont(QFont("Arial", 24))

        name = self.image_data["text"]["charaName"]
        self.name_text = self.scene.addText(name)
        self.name_text.setDefaultTextColor(QColor(255, 255, 255))
        self.name_text.setPos(25, 615)
        self.name_text.setZValue(100)
        self.name_text.setFont(QFont("Arial", 55))

        daytimeText = self.image_data["ui"]["time"]
        self.time_text = self.scene.addText(daytimeText)
        self.time_text.setDefaultTextColor(QColor(255, 255, 255))
        self.time_text.setPos(1300, 20)
        self.time_text.setZValue(100)
        self.time_text.setFont(QFont("Arial", 40))

        chapterText = self.image_data["ui"]["chapter"]
        self.chapter_text = self.scene.addText(chapterText)
        self.chapter_text.setDefaultTextColor(QColor(255, 255, 255))
        self.chapter_text.setPos(1200, 77)
        self.chapter_text.setZValue(100)
        self.chapter_text.setFont(QFont("Arial", 30))

    def toggle_animation(self):
        if not self.animation_active:
            self.start_animation()
            self.button_start_animation.setText("Stop Animation")
        else:
            self.stop_animation()
            self.button_start_animation.setText("Start Animation")
        self.animation_active = not self.animation_active

    def start_animation(self):
        self.elapsed_timer = QElapsedTimer()
        self.elapsed_timer.start()
        self.global_timer = QTimer(self)
        self.global_timer.timeout.connect(self.update_animation)
        self.global_timer.start(33)  # 33 ms для 30 FPS

    def update_animation(self):
        elapsed_time = self.elapsed_timer.elapsed()

        # Флаг для остановки анимации, когда она завершится
        all_animations_done = True

        # Анимация фона
        background_info = self.image_data.get("background", {})
        if background_info.get("animation"):
            duration = background_info["animationSettings"]["time"]
            if elapsed_time < duration:
                all_animations_done = False

                start_pos = QPointF(background_info["position"]["x"], background_info["position"]["y"])
                target_pos = QPointF(background_info["animationSettings"]["position"]["x"], background_info["animationSettings"]["position"]["y"])
                progress = elapsed_time / duration

                # Здесь можно добавить функцию плавности (easing function)
                eased_progress = self.ease_in_out_quad(progress)

                new_x = start_pos.x() + eased_progress * (target_pos.x() - start_pos.x())
                new_y = start_pos.y() + eased_progress * (target_pos.y() - start_pos.y())

                self.background_item.setPos(QPointF(new_x, new_y))

        # Анимация спрайтов
        for item, image_info in self.image_items:
            if image_info.get("animation"):
                duration = image_info["animationSettings"]["time"]
                if elapsed_time < duration:
                    all_animations_done = False

                    start_pos = QPointF(image_info["position"]["x"], image_info["position"]["y"])
                    target_pos = QPointF(image_info["animationSettings"]["position"]["x"], image_info["animationSettings"]["position"]["y"])
                    progress = elapsed_time / duration

                    # Функция плавности
                    eased_progress = self.ease_in_out_quad(progress)

                    new_x = start_pos.x() + eased_progress * (target_pos.x() - start_pos.x())
                    new_y = start_pos.y() + eased_progress * (target_pos.y() - start_pos.y())

                    item.setPos(QPointF(new_x, new_y))

        # Останавливаем анимацию, если все движения завершены
        if all_animations_done:
            self.stop_animation()
            self.button_start_animation.setText("Start Animation")
            self.animation_active = False

    def stop_animation(self):
        if hasattr(self, 'global_timer'):
            self.global_timer.stop()

        self.load_images()

    def ease_in_out_quad(self, t):
        """Функция плавности для более гладкой анимации."""
        if t < 0.5:
            return 2 * t * t
        else:
            return -1 + (4 - 2 * t) * t

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, scene, parent=None):
        super().__init__(scene, parent)
        self.scale_factor = 1.0
        self.min_scale = 0.5
        self.max_scale = 2.0

    def wheelEvent(self, event: QWheelEvent):
        delta = event.angleDelta().y() / 120
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
