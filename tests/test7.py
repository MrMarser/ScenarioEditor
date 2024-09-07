import sys
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsPixmapItem, QMainWindow
from PyQt6.QtGui import QPixmap, QPen, QColor
from PyQt6.QtCore import Qt, QRectF, QPointF

class ResizableRectItem(QGraphicsRectItem):
    def __init__(self, pixmap_item):
        super().__init__(pixmap_item.boundingRect())
        self.setPen(QPen(QColor(0, 255, 0), 2))
        self.setFlags(QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable |
                      QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsRectItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.pixmap_item = pixmap_item
        self.setParentItem(pixmap_item)

    def mousePressEvent(self, event):
        self._drag_start_pos = event.pos()
        self._rect_start_size = self.rect()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            diff = event.pos() - self._drag_start_pos
            new_rect = QRectF(self._rect_start_size)
            new_rect.setWidth(self._rect_start_size.width() + diff.x())
            new_rect.setHeight(self._rect_start_size.height() + diff.y())
            self.setRect(new_rect)
            self.pixmap_item.setPixmap(self.pixmap_item.pixmap().scaled(new_rect.size().toSize(), Qt.AspectRatioMode.KeepAspectRatio))
        super().mouseMoveEvent(event)

class ImageEditor(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(QGraphicsView.RenderHint.Antialiasing)

        # Загрузка изображения
        pixmap = QPixmap('image1.png')  # Замените на путь к вашему изображению
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        # Добавление рамки вокруг изображения
        resizable_rect = ResizableRectItem(pixmap_item)
        self.scene.addItem(resizable_rect)

    def wheelEvent(self, event):
        # Масштабирование холста
        if event.angleDelta().y() > 0:
            self.scale(1.1, 1.1)
        else:
            self.scale(0.9, 0.9)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Editor with Resizable Frame")
        self.setCentralWidget(ImageEditor())

app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
