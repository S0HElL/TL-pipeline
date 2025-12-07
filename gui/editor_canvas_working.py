"""
Manga Translator GUI - Working Editor Canvas
Interactive image display and text editing canvas with reliable resizeable bounding boxes.
"""

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsPixmapItem, QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF
from PySide6.QtGui import (
    QPixmap, QImage, QPainter, QPen, QBrush, QColor, QFont
)
from PIL import Image


class WorkingBoundingBoxItem(QGraphicsRectItem):
    """
    Working resizable bounding box for text regions.
    Uses Qt's built-in resize mechanism for reliability.
    """
    
    def __init__(self, rect, data, parent=None):
        super().__init__(rect, parent)
        self.data = data
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        self.setFlag(QGraphicsItem.ItemIsResizable, True)  # Enable Qt's built-in resize
        
        # Visual properties
        self.default_pen = QPen(QColor(0, 255, 0), 2)
        self.selected_pen = QPen(QColor(255, 255, 0), 3)
        self.hover_pen = QPen(QColor(0, 255, 255), 2)
        
        self.setPen(self.default_pen)
        self.setBrush(QBrush(Qt.NoBrush))
        
        # Text preview
        self.text_item = None
        self.create_text_preview()
        
    def create_text_preview(self):
        """Create text preview item for the bounding box."""
        self.text_item = QGraphicsTextItem(self.data.get('english_text', ''), self)
        self.text_item.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.text_item.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.text_item.setFlag(QGraphicsItem.ItemStacksBehindParent, True)
        
        # Set text properties
        font = QFont("Arial", 12)
        self.text_item.setFont(font)
        self.text_item.setDefaultTextColor(QColor(0, 0, 0))
        
        # Position text in center of bounding box
        self.update_text_position()
        
    def update_text_position(self):
        """Update the position of the text preview."""
        if self.text_item and self.rect().isValid():
            rect = self.rect()
            text_rect = self.text_item.boundingRect()
            
            x = rect.x() + (rect.width() - text_rect.width()) / 2
            y = rect.y() + (rect.height() - text_rect.height()) / 2
            
            self.text_item.setPos(x, y)
            
    def update_text_content(self, text):
        """Update the text content of the preview."""
        if self.text_item:
            self.text_item.setPlainText(text)
            self.update_text_position()
            
    def update_text_style(self, font_family=None, font_size=None, alignment=None, color=None):
        """Update the text styling."""
        if self.text_item:
            font = QFont()
            if font_family:
                font.setFamily(font_family)
            if font_size:
                font.setPointSize(font_size)
            self.text_item.setFont(font)
            
            if color:
                self.text_item.setDefaultTextColor(QColor(color))
                
            if alignment == "Center":
                self.text_item.setAlignment(Qt.AlignCenter)
            elif alignment == "Left":
                self.text_item.setAlignment(Qt.AlignLeft)
            elif alignment == "Right":
                self.text_item.setAlignment(Qt.AlignRight)
                
            self.update_text_position()
            
    def itemChange(self, change, value):
        """Handle item changes (movement, selection, etc.)."""
        if change == QGraphicsItem.ItemSelectedChange:
            if value:
                self.setPen(self.selected_pen)
            else:
                self.setPen(self.default_pen)
                
        elif change == QGraphicsItem.ItemPositionChange:
            # Update text position when moved
            self.update_text_position()
            
        elif change == QGraphicsItem.ItemParentChange:
            # Update text position when parent changes
            self.update_text_position()
            
        elif change == QGraphicsItem.ItemTransformChange:
            # Update text position when transformed
            self.update_text_position()
            
        return super().itemChange(change, value)
        
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            self.setSelected(True)
        super().mousePressEvent(event)
        
    def hoverEnterEvent(self, event):
        """Handle hover enter events."""
        if not self.isSelected():
            self.setPen(self.hover_pen)
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """Handle hover leave events."""
        if not self.isSelected():
            self.setPen(self.default_pen)
        super().hoverLeaveEvent(event)


class WorkingEditorCanvas(QGraphicsView):
    """
    Working main canvas for image display and text editing.
    
    Features:
    - Image loading and display with zoom/pan
    - Working resizable bounding box editing
    - Text preview rendering
    - Fixed text style updates
    - Uses Qt's built-in resize functionality
    """
    
    # Signals
    selection_changed = Signal(object)  # Emits selected bounding box data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Image properties
        self.original_pixmap = None
        self.current_pixmap = None
        self.image_rect = QRectF()
        
        # Bounding boxes
        self.bounding_boxes = []
        self.selected_box_index = -1
        
        # View settings
        self.zoom_factor = 1.0
        self.min_zoom = 0.1
        self.max_zoom = 5.0
        
        # Text style settings
        self.current_font_family = "Arial"
        self.current_font_size = 20
        self.current_alignment = "Center"
        self.current_text_color = "#000000"
        
        self.setup_view()
        
    def setup_view(self):
        """Setup the view properties."""
        # Enable antialiasing
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # Set scene rect large enough to accommodate images
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        
        # Set viewport update mode
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        
        # Background settings
        self.setBackgroundBrush(QBrush(Qt.lightGray))
        
        # Enable mouse tracking
        self.setMouseTracking(True)
        
        # Enable rubber band drag for selection
        self.setDragMode(QGraphicsView.RubberBandDrag)
        
    def load_image(self, image_path):
        """Load an image from file path."""
        try:
            # Load image using PIL first
            pil_image = Image.open(image_path)
            pil_image = pil_image.convert("RGB")
            
            # Convert to QImage
            qimage = QImage(
                pil_image.tobytes(), 
                pil_image.width, 
                pil_image.height, 
                pil_image.width * 3, 
                QImage.Format_RGB888
            )
            
            # Convert to QPixmap
            self.original_pixmap = QPixmap.fromImage(qimage)
            self.current_pixmap = QPixmap(self.original_pixmap)
            
            # Clear previous content
            self.scene.clear()
            self.bounding_boxes.clear()
            self.selected_box_index = -1
            
            # Add image to scene
            self.scene.addPixmap(self.current_pixmap)
            
            # Store image rect for boundary checking
            self.image_rect = QRectF(0, 0, self.current_pixmap.width(), self.current_pixmap.height())
            
            # Fit image in view
            self.fit_to_image()
            
            # Clear selection
            self.selection_changed.emit(None)
            
        except Exception as e:
            print(f"Error loading image: {e}")
            
    def fit_to_image(self):
        """Fit the image to the current view."""
        if self.current_pixmap:
            self.fitInView(self.image_rect, Qt.KeepAspectRatio)
            self.zoom_factor = 1.0
            
    def set_inpainted_image(self, pil_image):
        """Set the inpainted image after translation."""
        try:
            # Convert PIL image to QPixmap
            qimage = QImage(
                pil_image.tobytes(),
                pil_image.width,
                pil_image.height,
                pil_image.width * 3,
                QImage.Format_RGB888
            )
            self.current_pixmap = QPixmap.fromImage(qimage)
            
            # Update scene
            items = self.scene.items()
            for item in items:
                if isinstance(item, QGraphicsPixmapItem):
                    self.scene.removeItem(item)
                    
            self.scene.addPixmap(self.current_pixmap)
            
        except Exception as e:
            print(f"Error setting inpainted image: {e}")
            
    def set_translation_data(self, translated_data_list):
        """Set the translation data and create bounding boxes."""
        self.translated_data = translated_data_list
        self.create_bounding_boxes()
        
    def create_bounding_boxes(self):
        """Create interactive bounding boxes for translated text."""
        if not hasattr(self, 'translated_data'):
            return
            
        for i, data in enumerate(self.translated_data):
            group_box = data['group_box']
            rect = QRectF(group_box[0], group_box[1], 
                         group_box[2] - group_box[0], 
                         group_box[3] - group_box[1])
            
            box_item = WorkingBoundingBoxItem(rect, data)
            self.scene.addItem(box_item)
            self.bounding_boxes.append(box_item)
            
    def mousePressEvent(self, event):
        """Handle mouse press events."""
        if event.button() == Qt.LeftButton:
            # Check if we clicked on a bounding box
            pos = self.mapToScene(event.position().toPoint())
            items = self.scene.items(pos)
            
            clicked_box = None
            for item in items:
                if isinstance(item, WorkingBoundingBoxItem):
                    clicked_box = item
                    break
                    
            if clicked_box:
                self.select_bounding_box(clicked_box)
            else:
                # Deselect all
                self.deselect_all()
                
        super().mousePressEvent(event)
        
    def select_bounding_box(self, box_item):
        """Select a bounding box and emit selection change."""
        # Deselect all others
        for box in self.bounding_boxes:
            if box != box_item:
                box.setSelected(False)
                
        # Select the target box
        box_item.setSelected(True)
        self.selected_box_index = self.bounding_boxes.index(box_item)
        
        # Emit selection changed signal
        data = {
            'index': self.selected_box_index,
            'english_text': box_item.data.get('english_text', ''),
            'japanese_text': box_item.data.get('japanese_text', ''),
            'group_box': box_item.data.get('group_box', (0, 0, 0, 0))
        }
        self.selection_changed.emit(data)
        
    def deselect_all(self):
        """Deselect all bounding boxes."""
        for box in self.bounding_boxes:
            box.setSelected(False)
            
        self.selected_box_index = -1
        self.selection_changed.emit(None)
        
    def wheelEvent(self, event):
        """Handle mouse wheel for zooming."""
        if event.modifiers() == Qt.ControlModifier:
            # Zoom with Ctrl+Wheel
            angle = event.angleDelta().y()
            factor = 1.2 if angle > 0 else 1/1.2
            
            # Get cursor position before zoom
            cursor_pos = self.mapToScene(event.position().toPoint())
            
            # Zoom
            self.zoom_factor *= factor
            self.zoom_factor = max(self.min_zoom, min(self.max_zoom, self.zoom_factor))
            
            self.scale(1/factor if angle > 0 else factor, 1/factor if angle > 0 else factor)
            
            # Keep cursor position stable
            new_cursor_pos = self.mapToScene(event.position().toPoint())
            delta = cursor_pos - new_cursor_pos
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() + int(delta.x())
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() + int(delta.y())
            )
            
            event.accept()
        else:
            # Normal scroll
            super().wheelEvent(event)
            
    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Delete and self.selected_box_index >= 0:
            # Delete selected bounding box
            self.delete_selected_box()
        elif event.key() == Qt.Key_Escape:
            # Deselect all
            self.deselect_all()
        else:
            super().keyPressEvent(event)
            
    def delete_selected_box(self):
        """Delete the currently selected bounding box."""
        if self.selected_box_index >= 0:
            box = self.bounding_boxes[self.selected_box_index]
            self.scene.removeItem(box)
            self.bounding_boxes.pop(self.selected_box_index)
            self.selected_box_index = -1
            self.selection_changed.emit(None)
            
    def update_text_style(self):
        """Update the text style for the selected bounding box."""
        if self.selected_box_index >= 0 and self.selected_box_index < len(self.bounding_boxes):
            box = self.bounding_boxes[self.selected_box_index]
            box.update_text_style(
                font_family=self.current_font_family,
                font_size=self.current_font_size,
                alignment=self.current_alignment,
                color=self.current_text_color
            )
            
    def update_text_preview(self, index, text):
        """Update text preview for a specific bounding box."""
        if 0 <= index < len(self.bounding_boxes):
            box = self.bounding_boxes[index]
            box.update_text_content(text)
            
    def get_final_image(self):
        """Get the final rendered image with all text applied."""
        if not self.current_pixmap:
            return None
            
        # Create a copy of the current image
        final_image = self.current_pixmap.toImage()
        painter = QPainter(final_image)
        
        # Render all bounding boxes with their current text
        for box in self.bounding_boxes:
            if box.text_item:
                # Get the text and position
                text = box.text_item.toPlainText()
                font = box.text_item.font()
                color = box.text_item.defaultTextColor()
                
                # Set font and color
                painter.setFont(font)
                painter.setPen(QPen(color))
                
                # Draw text at the box's text position
                rect = box.rect()
                
                # Handle alignment
                if box.text_item.alignment() == Qt.AlignCenter:
                    text_rect = box.text_item.boundingRect()
                    x = rect.x() + (rect.width() - text_rect.width()) / 2
                    y = rect.y() + (rect.height() - text_rect.height()) / 2
                elif box.text_item.alignment() == Qt.AlignLeft:
                    x = rect.x() + 5
                    y = rect.y() + rect.height() / 2
                else:  # Right alignment
                    text_rect = box.text_item.boundingRect()
                    x = rect.x() + rect.width() - text_rect.width() - 5
                    y = rect.y() + rect.height() / 2
                    
                # Draw text with outline for better readability
                painter.setPen(QPen(Qt.white, 2))
                painter.drawText(QPointF(x, y + font.pointSize()), text)
                painter.setPen(QPen(color))
                painter.drawText(QPointF(x, y + font.pointSize()), text)
                
        painter.end()
        
        # Convert back to PIL Image
        try:
            from PIL import ImageQt
            return ImageQt.fromqimage(final_image)
        except ImportError:
            # Fallback: return QImage if ImageQt is not available
            return final_image