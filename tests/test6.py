import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QGraphicsItem
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QBrush, QCursor
from PyQt6.QtCore import Qt, QRectF, QPointF, QSize

class ResizablePixmapItem(QGraphicsPixmapItem):
    def __init__(self, pixmap):
        super().__init__(pixmap)
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
                      QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)
        self.resize_handle_size = 10
        self.resizing = False
        self.resize_corner = None
        self.original_pixmap = pixmap
        self.cursor_resize = QCursor(Qt.CursorShape.SizeFDiagCursor)
        self.cursor_default = QCursor(Qt.CursorShape.ArrowCursor)
        self.min_scale_factor = 0.1  # Минимальный коэффициент масштабирования
        self.max_scale_factor = 5.0  # Максимальный коэффициент масштабирования

    def boundingRect(self):
        rect = super().boundingRect()
        return rect.adjusted(-self.resize_handle_size, -self.resize_handle_size, self.resize_handle_size, self.resize_handle_size)

    def shape(self):
        path = super().shape()
        rect = self.boundingRect()
        path.addRect(rect)
        return path

    def paint(self, painter, option, widget):
        super().paint(painter, option, widget)
        if self.isSelected():
            # Получаем текущий масштаб
            scale = self.get_current_scale()

            pen = QPen(QColor(255, 0, 0), 2 * scale)
            painter.setPen(pen)
            rect = self.boundingRect()
            painter.drawRect(rect)
            self.draw_resize_handles(painter, scale)

    def draw_resize_handles(self, painter, scale):
        brush = QBrush(QColor(255, 0, 0))
        painter.setBrush(brush)
        rect = self.boundingRect()
        handle_size = self.resize_handle_size * scale

        # Draw resize handles at 8 points
        points = [
            QPointF(rect.left(), rect.top()),  # Top-left
            QPointF(rect.left() + rect.width() / 2, rect.top()),  # Top-center
            QPointF(rect.right(), rect.top()),  # Top-right
            QPointF(rect.right(), rect.top() + rect.height() / 2),  # Right-center
            QPointF(rect.right(), rect.bottom()),  # Bottom-right
            QPointF(rect.left() + rect.width() / 2, rect.bottom()),  # Bottom-center
            QPointF(rect.left(), rect.bottom()),  # Bottom-left
            QPointF(rect.left(), rect.top() + rect.height() / 2)  # Left-center
        ]

        for point in points:
            painter.drawRect(QRectF(point.x() - handle_size / 2, point.y() - handle_size / 2, handle_size, handle_size))

    def get_current_scale(self):
        # Вычисляем текущий масштаб на основе исходного и текущего размеров
        current_width = self.boundingRect().width()
        original_width = self.original_pixmap.width()
        return current_width / original_width

    def hoverMoveEvent(self, event):
        if self.is_resizing_zone(event.pos()):
            self.setCursor(self.cursor_resize)
        else:
            self.setCursor(self.cursor_default)
        super().hoverMoveEvent(event)

    def is_resizing_zone(self, pos):
        rect = self.boundingRect()
        handle_size = self.resize_handle_size * self.get_current_scale()

        return any([
            QRectF(rect.left() - handle_size / 2, rect.top() - handle_size / 2, handle_size, handle_size).contains(pos),  # Top-left
            QRectF(rect.left() + rect.width() / 2 - handle_size / 2, rect.top() - handle_size / 2, handle_size, handle_size).contains(pos),  # Top-center
            QRectF(rect.right() - handle_size / 2, rect.top() - handle_size / 2, handle_size, handle_size).contains(pos),  # Top-right
            QRectF(rect.right() - handle_size / 2, rect.top() + rect.height() / 2 - handle_size / 2, handle_size, handle_size).contains(pos),  # Right-center
            QRectF(rect.right() - handle_size / 2, rect.bottom() - handle_size / 2, handle_size, handle_size).contains(pos),  # Bottom-right
            QRectF(rect.left() + rect.width() / 2 - handle_size / 2, rect.bottom() - handle_size / 2, handle_size, handle_size).contains(pos),  # Bottom-center
            QRectF(rect.left() - handle_size / 2, rect.bottom() - handle_size / 2, handle_size, handle_size).contains(pos),  # Bottom-left
            QRectF(rect.left() - handle_size / 2, rect.top() + rect.height() / 2 - handle_size / 2, handle_size, handle_size).contains(pos)  # Left-center
        ])

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_resizing_zone(event.pos()):
                self.resizing = True
                self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, False)
                self.resize_corner = self.get_resize_corner(event.pos())
            else:
                self.resizing = False
        super().mousePressEvent(event)

    def get_resize_corner(self, pos):
        rect = self.boundingRect()
        handle_size = self.resize_handle_size * self.get_current_scale()

        if QRectF(rect.left() - handle_size / 2, rect.top() - handle_size / 2, handle_size, handle_size).contains(pos):
            return 'top_left'
        elif QRectF(rect.left() + rect.width() / 2 - handle_size / 2, rect.top() - handle_size / 2, handle_size, handle_size).contains(pos):
            return 'top_center'
        elif QRectF(rect.right() - handle_size / 2, rect.top() - handle_size / 2, handle_size, handle_size).contains(pos):
            return 'top_right'
        elif QRectF(rect.right() - handle_size / 2, rect.top() + rect.height() / 2 - handle_size / 2, handle_size, handle_size).contains(pos):
            return 'right_center'
        elif QRectF(rect.right() - handle_size / 2, rect.bottom() - handle_size / 2, handle_size, handle_size).contains(pos):
            return 'bottom_right'
        elif QRectF(rect.left() + rect.width() / 2 - handle_size / 2, rect.bottom() - handle_size / 2, handle_size, handle_size).contains(pos):
            return 'bottom_center'
        elif QRectF(rect.left() - handle_size / 2, rect.bottom() - handle_size / 2, handle_size, handle_size).contains(pos):
            return 'bottom_left'
        elif QRectF(rect.left() - handle_size / 2, rect.top() + rect.height() / 2 - handle_size / 2, handle_size, handle_size).contains(pos):
            return 'left_center'
        return None

    def mouseMoveEvent(self, event):
        if self.resizing:
            self.resize_item(event.pos(), event.modifiers() & Qt.KeyboardModifier.ControlModifier)
        else:
            super().mouseMoveEvent(event)

    def resize_item(self, pos, keep_aspect_ratio):
        rect = self.boundingRect()
        new_rect = QRectF(rect)

        if self.resize_corner == 'top_left':
            new_rect.setTopLeft(pos)
        elif self.resize_corner == 'top_center':
            new_rect.setTop(pos.y())
        elif self.resize_corner == 'top_right':
            new_rect.setTopRight(pos)
        elif self.resize_corner == 'right_center':
            new_rect.setRight(pos.x())
        elif self.resize_corner == 'bottom_right':
            new_rect.setBottomRight(pos)
        elif self.resize_corner == 'bottom_center':
            new_rect.setBottom(pos.y())
        elif self.resize_corner == 'bottom_left':
            new_rect.setBottomLeft(pos)
        elif self.resize_corner == 'left_center':
            new_rect.setLeft(pos.x())

        # Применение ограничений на масштабирование
        original_width = self.original_pixmap.width()
        original_height = self.original_pixmap.height()

        new_width = max(original_width * self.min_scale_factor, min(new_rect.width(), original_width * self.max_scale_factor))
        new_height = max(original_height * self.min_scale_factor, min(new_rect.height(), original_height * self.max_scale_factor))

        if self.resize_corner in ['top_center', 'bottom_center']:
            new_rect.setHeight(new_height)
        elif self.resize_corner in ['left_center', 'right_center']:
            new_rect.setWidth(new_width)
        else:
            new_rect.setWidth(new_width)
            new_rect.setHeight(new_height)

        if keep_aspect_ratio:
            aspect_ratio = self.original_pixmap.width() / self.original_pixmap.height()
            if self.resize_corner in ['top_left', 'bottom_left', 'top_right', 'bottom_right']:
                if new_width / new_height > aspect_ratio:
                    new_width = new_height * aspect_ratio
                else:
                    new_height = new_width / aspect_ratio

                if self.resize_corner in ['top_left', 'bottom_left']:
                    new_rect.setLeft(new_rect.right() - new_width)
                else:
                    new_rect.setRight(new_rect.left() + new_width)

                if self.resize_corner in ['top_left', 'top_right']:
                    new_rect.setTop(new_rect.bottom() - new_height)
                else:
                    new_rect.setBottom(new_rect.top() + new_height)

        self.prepareGeometryChange()
        self.setPixmap(self.original_pixmap.scaled(int(new_rect.width()), int(new_rect.height()), Qt.AspectRatioMode.IgnoreAspectRatio))
        self.setOffset(new_rect.topLeft() - rect.topLeft())

    def mouseReleaseEvent(self, event):
        self.resizing = False
        self.resize_corner = None
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
        super().mouseReleaseEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Рабочая зона")
        self.setGeometry(100, 100, 1600, 900)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(0, 0, 1600, 900)
        self.setCentralWidget(self.view)

        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)

        self.view.setBackgroundBrush(QBrush(Qt.GlobalColor.white))

        # Добавляем рабочую зону
        self.add_workspace()

        # Минимальный и максимальный уровни масштабирования
        self.min_scale = 0.1
        self.max_scale = 5.0

    def add_workspace(self):
        brush = QBrush(QColor(211, 211, 211))  # Светло-серый цвет
        boundary_rect = QGraphicsRectItem(0, 0, 1600, 900)
        boundary_rect.setBrush(brush)
        boundary_rect.setPen(QPen(Qt.PenStyle.NoPen))  # Без границ
        self.scene.addItem(boundary_rect)

    def wheelEvent(self, event):
        zoom_in_factor = 1.1
        zoom_out_factor = 1 / zoom_in_factor

        current_scale = self.view.transform().m11()  # Получаем текущий уровень масштабирования

        if event.angleDelta().y() > 0:
            zoom_factor = zoom_in_factor
        else:
            zoom_factor = zoom_out_factor

        new_scale = current_scale * zoom_factor

        if self.min_scale <= new_scale <= self.max_scale:
            self.view.scale(zoom_factor, zoom_factor)

    def add_image(self, image_path):
        pixmap = QPixmap(image_path)
        item = ResizablePixmapItem(pixmap)
        self.scene.addItem(item)
        return item

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    # Добавление тестовых изображений
    item1 = window.add_image("tests/Amaya_acrid1.png")  # Замените на путь к вашему первому изображению
    item2 = window.add_image("tests/Amaya_acrid1.png")  # Замените на путь к вашему второму изображению

    sys.exit(app.exec())
