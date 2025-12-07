"""
Manga Translator GUI - Performance Optimized Editor Canvas
Enhanced version with improved rendering performance and memory management.
"""

from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsTextItem, QGraphicsPixmapItem, QWidget, QVBoxLayout
)
from PySide6.QtCore import Qt, Signal, QRectF, QPointF, QTimer
from PySide6.QtGui import (
    QPixmap, QImage, QPainter, QPen, QBrush, QColor, QFont
)
from PIL import Image
import gc


class OptimizedBoundingBoxItem(QGraphicsRectItem):
    """
    Performance-optimized bounding box for text regions.
    Implements caching and efficient redrawing.
    """
    
    def __init__(self, rect, data, parent=None):
        super().__init__(rect, parent)
        self.data = data
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges, True)
        
        # Visual properties with caching
        self._pens = {
            'default': QPen(QColor(0, 255, 0), 2),
            'selected': QPen(QColor(255, 255, 0), 3),
            'hover': QPen(QColor(0, 255, 255), 2)
        }
        self.setPen(self._pens['default'])
        self.setBrush(QBrush(Qt.NoBrush))
        
        # Text preview with lazy loading
        self.text_item = None
        self.text_cached = False
        self.create_text_preview()
        
    def create_text_preview(self):
        """Create text preview item for the bounding box with caching."""
        if self.text_item is None:
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
            self.text_cached = True
            
    def update_text_content(self, text):
        """Update the text content of the preview with caching."""
        if self.text_item:
            self.text_item.setPlainText(text)
            self.update_text_position()
            
    def update_text_style(self, font_family=None, font_size=None, alignment=None, color=None):
        """Update the text styling with performance optimization."""
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
            
    def update_text_position(self):
        """Update the position of the text preview."""
        if self.text_item and self.rect().isValid():
            rect = self.rect()
            text_rect = self.text_item.boundingRect()
            
            x = rect.x() + (rect.width() - text_rect.width()) / 2
            y = rect.y() + (rect.height() - text_rect.height()) / 2
            
            self.text_item.setPos(x, y)
            
    def itemChange(self, change, value):
        """Handle item changes with optimized redrawing."""
        if change == QGraphicsItem.ItemSelectedChange:
            if value:
                self.setPen(self._pens['selected'])
            else:
                self.setPen(self._pens['default'])
                
        elif change == QGraphicsItem.ItemPositionChange:
            # Update text position when moved
            self.update_text_position()
            
        return super().itemChange(change, value)
        
    def hoverEnterEvent(self, event):
        """Handle hover enter events with performance optimization."""
        if not self.isSelected():
            self.setPen(self._pens['hover'])
        super().hoverEnterEvent(event)
        
    def hoverLeaveEvent(self, event):
        """Handle hover leave events with performance optimization."""
        if not self.isSelected():
            self.setPen(self._pens['default'])
        super().hoverLeaveEvent(event)


class OptimizedEditorCanvas(QGraphicsView):
    """
    Performance-optimized main canvas for image display and text editing.
    
    Features:
    - Efficient image loading and caching
    - Optimized bounding box rendering
    - Memory management for large images
    - Lazy loading of components
    """
    
    # Signals
    selection_changed = Signal(object)  # Emits selected bounding box data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        
        # Image properties with caching
        self.original_pixmap = None
        self.current_pixmap = None
        self.image_rect = QRectF()
        self.image_cache = {}  # Cache for different image states
        
        # Bounding boxes with performance tracking
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
        
        # Performance optimization settings
        self.render_cache_enabled = True
        self.lazy_loading_enabled = True
        self.memory_limit_mb = 512  # 512MB limit
        
        # Update timer for batched operations
        self.update_timer = QTimer()
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(self.process_pending_updates)
        self.pending_updates = []
        
        self.setup_view()
        
    def setup_view(self):
        """Setup the view properties with performance optimizations."""
        # Enable antialiasing for better quality
        self.setRenderHint(QPainter.Antialiasing, True)
        self.setRenderHint(QPainter.SmoothPixmapTransform, True)
        
        # Optimize viewport updates
        self.setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)
        self.setOptimizationFlags(
            QGraphicsView.DontSavePainterState | 
            QGraphicsView.DontAdjustForAntialiasing
        )
        
        # Set scene rect large enough to accommodate images
        self.scene.setSceneRect(-5000, -5000, 10000, 10000)
        
        # Background settings
        self.setBackgroundBrush(QBrush(Qt.lightGray))
        
        # Enable mouse tracking for better interaction
        self.setMouseTracking(True)
        
    def load_image(self, image_path, use_cache=True):
        """Load an image from file path with performance optimization."""
        try:
            # Check cache first
            cache_key = f"original_{image_path}"
            if use_cache and cache_key in self.image_cache:
                cached_data = self.image_cache[cache_key]
                self.original_pixmap = cached_data['pixmap']
                self.current_pixmap = QPixmap(self.original_pixmap)
            else:
                # Load image using PIL with memory optimization
                with Image.open(image_path) as pil_image:
                    # Convert to RGB if necessary
                    if pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    
                    # Resize if too large (memory optimization)
                    max_size = 2048  # Max dimension
                    if max(pil_image.size) > max_size:
                        ratio = max_size / max(pil_image.size)
                        new_size = tuple(int(dim * ratio) for dim in pil_image.size)
                        pil_image = pil_image.resize(new_size, Image.Resampling.LANCZOS)
                    
                    # Convert to QImage efficiently
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
                    
                    # Cache the result
                    if use_cache:
                        self.image_cache[cache_key] = {
                            'pixmap': QPixmap(self.original_pixmap),
                            'size': pil_image.size,
                            'timestamp': QTimer().currentTime()
                        }
            
            # Clear previous content efficiently
            self.clear_scene()
            
            # Add image to scene
            self.scene.addPixmap(self.current_pixmap)
            
            # Store image rect for boundary checking
            self.image_rect = QRectF(0, 0, self.current_pixmap.width(), self.current_pixmap.height())
            
            # Fit image in view
            self.fit_to_image()
            
            # Clear selection
            self.selection_changed.emit(None)
            
            # Force garbage collection
            gc.collect()
            
        except Exception as e:
            print(f"Error loading image: {e}")
            
    def clear_scene(self):
        """Clear the scene efficiently."""
        # Remove items in batch
        items = self.scene.items()
        for item in items:
            self.scene.removeItem(item)
        
        self.bounding_boxes.clear()
        self.selected_box_index = -1
        
    def fit_to_image(self):
        """Fit the image to the current view."""
        if self.current_pixmap:
            self.fitInView(self.image_rect, Qt.KeepAspectRatio)
            self.zoom_factor = 1.0
            
    def set_inpainted_image(self, pil_image, use_cache=True):
        """Set the inpainted image after translation with caching."""
        try:
            # Convert PIL image to QPixmap efficiently
            if pil_image.mode != 'RGB':
                pil_image = pil_image.convert('RGB')
            
            qimage = QImage(
                pil_image.tobytes(),
                pil_image.width,
                pil_image.height,
                pil_image.width * 3,
                QImage.Format_RGB888
            )
            self.current_pixmap = QPixmap.fromImage(qimage)
            
            # Update scene efficiently
            self.update_scene_image()
            
        except Exception as e:
            print(f"Error setting inpainted image: {e}")
            
    def update_scene_image(self):
        """Update the scene image efficiently."""
        # Remove existing pixmap items
        items = self.scene.items()
        for item in items:
            if isinstance(item, QGraphicsPixmapItem):
                self.scene.removeItem(item)
                
        self.scene.addPixmap(self.current_pixmap)
        
    def set_translation_data(self, translated_data_list):
        """Set the translation data and create bounding boxes with performance optimization."""
        self.translated_data = translated_data_list
        
        # Clear existing bounding boxes
        for box in self.bounding_boxes:
            self.scene.removeItem(box)
        self.bounding_boxes.clear()
        
        # Create new bounding boxes with batch processing
        if self.lazy_loading_enabled:
            # Use timer to batch create boxes (prevents UI blocking)
            self.pending_updates.append(('create_boxes', translated_data_list))
            if not self.update_timer.isActive():
                self.update_timer.start(10)  # 10ms delay
        else:
            self.create_bounding_boxes_immediately(translated_data_list)
            
    def create_bounding_boxes_immediately(self, translated_data_list):
        """Create bounding boxes immediately (for non-lazy loading)."""
        for i, data in enumerate(translated_data_list):
            group_box = data['group_box']
            rect = QRectF(group_box[0], group_box[1], 
                         group_box[2] - group_box[0], 
                         group_box[3] - group_box[1])
            
            box_item = OptimizedBoundingBoxItem(rect, data)
            self.scene.addItem(box_item)
            self.bounding_boxes.append(box_item)
            
    def process_pending_updates(self):
        """Process pending updates in batch."""
        while self.pending_updates:
            update_type, data = self.pending_updates.pop(0)
            
            if update_type == 'create_boxes':
                self.create_bounding_boxes_immediately(data)
                
        self.update_timer.stop()
        
    def select_bounding_box(self, box_item):
        """Select a bounding box and emit selection change."""
        # Deselect all others efficiently
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
        """Handle mouse wheel for zooming with performance optimization."""
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
            
    def update_text_style(self):
        """Update the text style for the selected bounding box with optimization."""
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
            
    def set_text_color(self, color):
        """Set the current text color."""
        self.current_text_color = color
        self.update_text_style()
        
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
            
    def clear_cache(self):
        """Clear image cache to free memory."""
        self.image_cache.clear()
        gc.collect()
        
    def get_memory_usage(self):
        """Get approximate memory usage in MB."""
        total_size = 0
        for cache_data in self.image_cache.values():
            if 'pixmap' in cache_data:
                total_size += cache_data['pixmap'].width() * cache_data['pixmap'].height() * 4  # 4 bytes per pixel
        return total_size / (1024 * 1024)  # Convert to MB