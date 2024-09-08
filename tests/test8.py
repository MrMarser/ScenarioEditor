import sys
import json
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import QTimer, QPointF, QRectF, QPoint, Qt
from PyQt6.QtGui import QPixmap, QPainter, QBrush, QColor, QWheelEvent, QTransform, QFont, QPolygon, QImage

# Пример JSON данных
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
                "time": 5000,
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
            "text": "qt.pointer.dispatch: skipping QEventPoint(id=1 ts=0 pos=0,0 scn=610.902,814.85 gbl=610.902,814.85 Released ellipse=(1x1 ∡ 0) vel=0,0 press=-610.902,-814.85 last=-610.902,-814.85 Δ 610.902,814.85) : no target windowыолуалдыаоыдлудылаоыдлаулдуоладыладлыалдоыnikitaguzarskij@MacBook-Pro-Nikita ScenarioEditor % "
        },
        "ui": {
            "time": "Afternoon",
            "chapter": " Prologue",
            "emotion": false,
            "charaEmotion": "",
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
                    "time": 5000,
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
                    "time": 5000,
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
                    "time": 5000,
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
        """Загружает фон и спрайты на сцену."""
        self.scene.clear()  # Очищаем всю сцену перед загрузкой новых элементов

        # Создаем белую область 1600x900
        white_background = self.scene.addRect(QRectF(0, 0, 1600, 900), brush=QBrush(QColor(255, 255, 255)))
        white_background.setZValue(-10)  # Устанавливаем белый фон на самое нижнее Z-значение

        # Загружаем фон
        background_info = self.image_data.get("background", {})
        if background_info:
            background_pixmap = QPixmap(background_info['name'])  # Путь к файлу фона
            if not background_pixmap.isNull():
                self.background_item = QGraphicsPixmapItem(background_pixmap)
                self.background_item.setPos(background_info["position"]["x"], background_info["position"]["y"])
                self.background_item.setTransform(QTransform().scale(background_info["scale"]["x"], background_info["scale"]["y"]))  # Масштабируем по x и y
                self.background_item.setZValue(-1)  # Z-значение для фона, чтобы он был ниже всех спрайтов
                self.scene.addItem(self.background_item)
            else:
                print(f"Failed to load background image: {background_info['name']}")
        else:
            self.background_item = None

        # Загружаем спрайты по порядку
        sprite_data = self.image_data.get("sprite", {})
        sprite_count = sprite_data.get("count", 0)
        self.image_items = []

        for i in range(sprite_count):
            sprite_info = sprite_data.get(str(i), {})
            if not sprite_info:
                continue

            sprite_pixmap = QPixmap(sprite_info['name'])  # Путь к файлу спрайта
            if sprite_pixmap.isNull():
                print(f"Failed to load sprite: {sprite_info['name']}")
                continue

            sprite_item = QGraphicsPixmapItem(sprite_pixmap)
            sprite_item.setPos(sprite_info["position"]["x"], sprite_info["position"]["y"])
            sprite_item.setTransform(QTransform().scale(sprite_info["scale"]["x"], sprite_info["scale"]["y"]))  # Масштабируем по обеим осям
            sprite_item.setZValue(i)  # Устанавливаем Z-значение для перекрытия: более поздние спрайты выше

            self.scene.addItem(sprite_item)
            self.image_items.append((sprite_item, sprite_info))  # сохраняем item и его параметры


        mhimage = "tests/HeroMainDialogueTheme.PNG"
        nmhimage = "tests/notNeroMainDialogueTheme.PNG"

        if self.image_data["text"]["charaName"] == "Макиширо Ямагаки":
            self.fixed_image = QGraphicsPixmapItem(QPixmap(mhimage))
        else:
            self.fixed_image = QGraphicsPixmapItem(QPixmap(nmhimage))

        self.fixed_image.setPos(0, 0)  # Устанавливаем позицию неподвижного изображения
        self.fixed_image.setZValue(99)  # Устанавливаем высокий Z-индекс для отображения поверх других элементов
        self.scene.addItem(self.fixed_image)  # Добавляем неподвижное изображение на сцену
        
        text = self.image_data["text"]["text"]
        self.text_item = self.scene.addText(text)  # Создаем текст
        self.text_item.setDefaultTextColor(QColor(255, 255, 255))  # Устанавливаем цвет текста
        self.text_item.setPos(25, 715)  # Устанавливаем позицию текста
        self.text_item.setTextWidth(1100)  # Ограничиваем ширину текста до 600 пикселей
        self.text_item.setZValue(100)  # Устанавливаем высокий Z-индекс, чтобы текст был поверх всего

        font = QFont("Arial", 24)  # Шрифт Arial, размер 24
        self.text_item.setFont(font)  # Применяем шрифт к текстовому элементу


        name = self.image_data["text"]["charaName"]
        self.name_text = self.scene.addText(name)
        self.name_text.setDefaultTextColor(QColor(255, 255, 255))
        self.name_text.setPos(25, 615)
        self.name_text.setZValue(100)

        font = QFont("Arial", 55)
        self.name_text.setFont(font)


        daytimeText = self.image_data["ui"]["time"]
        self.time_text = self.scene.addText(daytimeText)
        self.time_text.setDefaultTextColor(QColor(255, 255, 255))
        self.time_text.setPos(1300, 20)
        self.time_text.setZValue(100)

        font = QFont("Arial", 40)
        self.time_text.setFont(font)


        chapterText = self.image_data["ui"]["chapter"]
        self.chapter_text = self.scene.addText(chapterText)
        self.chapter_text.setDefaultTextColor(QColor(255, 255, 255))
        self.chapter_text.setPos(1200, 77)
        self.chapter_text.setZValue(100)

        font = QFont("Arial", 30)
        self.chapter_text.setFont(font)


        def invert_mask(mask_pixmap):
            mask_image = mask_pixmap.toImage()  # Преобразуем QPixmap в QImage для обработки
            inverted_image = QImage(mask_image.size(), QImage.Format.Format_Mono)

            # Инвертируем цвета пикселей
            for y in range(mask_image.height()):
                for x in range(mask_image.width()):
                    pixel_color = mask_image.pixelColor(x, y)
                    if pixel_color == QColor(255, 255, 255):  # Если белый пиксель
                        inverted_image.setPixel(x, y, 0)  # Прозрачный (черный)
                    else:
                        inverted_image.setPixel(x, y, 1)  # Непрозрачный (белый)

            # Преобразуем обратно в QPixmap
            return QPixmap.fromImage(inverted_image)

        # Загружаем charaEmotionBackground и применяем маску
        chara_emotion_background = self.image_data["ui"].get("charaEmotionBackground", None)
        if chara_emotion_background:
            emotion_bg_pixmap = QPixmap(chara_emotion_background)
            if not emotion_bg_pixmap.isNull():
                # Применяем позицию и масштаб
                emotion_bg_pos = self.image_data["ui"].get("charaEmotionBackgroundPosition", {"x": 0, "y": 0})
                emotion_bg_scale = self.image_data["ui"].get("charaEmotionBackgroundScale", {"x": 4.0, "y": 4.0})

                # Изменяем размер изображения
                scaled_pixmap = emotion_bg_pixmap.scaled(
                    int(emotion_bg_pixmap.width() * emotion_bg_scale["x"]),
                    int(emotion_bg_pixmap.height() * emotion_bg_scale["y"])
                )


                self.chara_emotion_background_item = QGraphicsPixmapItem(scaled_pixmap)
                self.chara_emotion_background_item.setPos(emotion_bg_pos["x"], emotion_bg_pos["y"])
                self.chara_emotion_background_item.setZValue(99)  # Устанавливаем Z-индекс для эмоционального фона

                # Создаем маску (например, трапецию)
                mask_polygon = QPolygon([QPoint(1300, 300), QPoint(1600, 500), QPoint(1600, 900), QPoint(1100, 900)])  # Пример трапеции
                
                # Создаем QPixmap для маски
                mask_pixmap = QPixmap(scaled_pixmap.size())
                mask_pixmap.fill(QColor(0, 0, 0, 0))  # Прозрачный фон для маски

                # Рисуем маску в виде полигона
                painter = QPainter(mask_pixmap)
                painter.setBrush(QColor(255, 255, 255))
                painter.drawPolygon(mask_polygon)
                painter.end()

                # Применяем маску к изображению
                scaled_pixmap.setMask(invert_mask(mask_pixmap).createMaskFromColor(QColor(255, 255, 255), Qt.MaskMode.MaskInColor))

                # Применяем изображение с маской
                self.chara_emotion_background_item.setPixmap(scaled_pixmap)

                self.scene.addItem(self.chara_emotion_background_item)
            else:
                print(f"Failed to load charaEmotionBackground image: {chara_emotion_background}")



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

        # Анимация для фона
        if self.background_item:
            background_info = self.image_data.get("background", {})
            if background_info.get("animation"):
                start_pos = self.background_item.pos()
                start_scale_x = self.background_item.transform().m11()  # Текущий масштаб по оси X
                start_scale_y = self.background_item.transform().m22()  # Текущий масштаб по оси Y

                animation_settings = background_info.get("animationSettings", {})
                target_x = animation_settings["position"].get("x", start_pos.x())
                target_y = animation_settings["position"].get("y", start_pos.y())
                target_scale_x = animation_settings["scale"].get("x", start_scale_x)
                target_scale_y = animation_settings["scale"].get("y", start_scale_y)
                duration = animation_settings.get("time", 1000)

                timer = QTimer(self)
                animate_function = self.create_animate_function(self.background_item, start_pos, start_scale_x, start_scale_y, target_x, target_y, target_scale_x, target_scale_y, timer, duration)
                timer.timeout.connect(animate_function)
                timer.start(16)
                self.timers.append(timer)

        # Анимация для спрайтов
        for item, image_info in self.image_items:
            start_pos = item.pos()
            start_scale_x = item.transform().m11()  # Текущий масштаб по оси X
            start_scale_y = item.transform().m22()  # Текущий масштаб по оси Y

            # Берем цели для анимации
            animation_settings = image_info.get("animationSettings", {})
            target_x = animation_settings["position"].get("x", start_pos.x())
            target_y = animation_settings["position"].get("y", start_pos.y())
            target_scale_x = animation_settings["scale"].get("x", start_scale_x)
            target_scale_y = animation_settings["scale"].get("y", start_scale_y)

            # Время анимации
            duration = animation_settings.get("time", 1000)

            timer = QTimer(self)
            start_time = 0
            interval = 10 

            animate_function = self.create_animate_function(item, start_pos, start_scale_x, start_scale_y, target_x, target_y, target_scale_x, target_scale_y, timer, duration)
            timer.timeout.connect(animate_function)
            timer.start(interval)
            self.timers.append(timer)  # Сохраняем таймер для остановки

    def stop_animation(self):
        # Останавливаем все таймеры
        for timer in self.timers:
            timer.stop()

        # Очищаем сцену и загружаем изображения заново
        self.load_images()

    def create_animate_function(self, item, start_pos, start_scale_x, start_scale_y, target_x, target_y, target_scale_x, target_scale_y, timer, duration):
        interval = 10 
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

            # Изменение масштаба по осям X и Y
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
