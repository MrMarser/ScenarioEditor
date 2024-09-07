from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QApplication, QVBoxLayout, QWidget, QPushButton, QListWidget, QListWidgetItem
from PyQt6.QtCore import QPointF, Qt, QRectF
from PyQt6.QtGui import QPixmap, QPen, QColor, QPainter
import sys

class GraphicsViewWithSelection(QGraphicsView):
    def __init__(self, scene, buffer_data, sprite_list_widget, parent=None):
        super().__init__(scene, parent)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setMouseTracking(True)
        self.selected_item = None
        self.selection_rect = None  # Рамка для выделения
        self.buffer_data = buffer_data
        self.sprite_list_widget = sprite_list_widget  # Правильный виджет списка

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if isinstance(item, QGraphicsPixmapItem):
            self.select_sprite(item)
        super().mousePressEvent(event)

    def select_sprite(self, item):
        if self.selection_rect is not None:
            self.scene().removeItem(self.selection_rect)  # Удаляем предыдущую рамку

        self.selected_item = item
        rect = self.selected_item.boundingRect()
        self.selection_rect = QGraphicsRectItem(rect)
        self.selection_rect.setPen(QPen(QColor(255, 0, 0), 2))  # Рамка вокруг спрайта
        self.selection_rect.setPos(self.selected_item.pos())  # Синхронизируем позицию с спрайтом
        self.scene().addItem(self.selection_rect)

        sprite_name = self.selected_item.data(0)  # Получаем имя спрайта
        
        # Выделение в списке
        for i in range(self.sprite_list_widget.count()):
            list_item = self.sprite_list_widget.item(i)
            if list_item.text() == sprite_name:
                self.sprite_list_widget.setCurrentItem(list_item)
                break

    def mouseMoveEvent(self, event):
        if self.selected_item is not None:
            new_pos = self.mapToScene(event.pos())
            self.selected_item.setPos(new_pos)
            self.selection_rect.setPos(new_pos)  # Перемещаем рамку вместе с спрайтом
            self.update_buffer_data(self.selected_item)
        super().mouseMoveEvent(event)

    def update_buffer_data(self, item):
        sprite_name = item.data(0)
        for key, sprite in self.buffer_data.items():
            if sprite["name"] == sprite_name:
                sprite["position"]["x"] = item.pos().x()
                sprite["position"]["y"] = item.pos().y()

class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.buffer_data = {
            "0": {"name": "tests/Amaya_acrid1.png", "position": {"x": 100, "y": 100}},
            "1": {"name": "tests/Amaya_acrid1.png", "position": {"x": 300, "y": 200}}
        }
        
        self.scene = QGraphicsScene(0, 0, 1600, 900)
        self.sprite_list_widget = QListWidget(self)  # Теперь правильный список
        self.sprite_list_widget.setMaximumWidth(200)
        self.sprite_list_widget.currentItemChanged.connect(self.on_sprite_list_selection_changed)

        self.view = GraphicsViewWithSelection(self.scene, self.buffer_data, self.sprite_list_widget)

        self.init_ui()
        self.populate_scene_with_sprites()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.addWidget(self.view)
        layout.addWidget(self.sprite_list_widget)
        self.setLayout(layout)

    def populate_scene_with_sprites(self):
        for key, sprite_data in self.buffer_data.items():
            pixmap = QPixmap(sprite_data["name"])  # Загружаем изображение
            item = QGraphicsPixmapItem(pixmap)
            item.setPos(QPointF(sprite_data["position"]["x"], sprite_data["position"]["y"]))
            item.setData(0, sprite_data["name"])  # Сохраняем имя спрайта для синхронизации
            self.scene.addItem(item)

            # Добавляем элемент в список
            list_item = QListWidgetItem(sprite_data["name"])
            self.sprite_list_widget.addItem(list_item)

    def on_sprite_list_selection_changed(self, current, previous):
        sprite_name = current.text()
        for item in self.scene.items():
            if isinstance(item, QGraphicsPixmapItem) and item.data(0) == sprite_name:
                self.view.select_sprite(item)
                break

app = QApplication(sys.argv)
main_window = MainWidget()
main_window.show()
sys.exit(app.exec())
