import os
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTreeView, QInputDialog, QFileDialog,
                            QFileSystemModel, QComboBox, QLineEdit, QMenu,
                            QMessageBox, QSplitter, QFrame, QApplication,
                            QProgressBar, QDialog, QSlider, QGroupBox)
from PySide6.QtCore import Qt, QDir, Signal, QTimer, QPoint, QRect, QSize, QMimeData
from PySide6.QtGui import (QPixmap, QImage, QAction, QDrag, QMouseEvent, 
                          QPainter, QColor, QPen)
from photo_editor.processing.image_operations import ImageProcessor, SegmentationParams

class FileNavigator(QWidget):
    file_selected = Signal(str)
    
    def __init__(self, start_path=None):
        super().__init__()
        self.start_path = start_path or r"C:\Users\colca\OneDrive\Pictures"
        self.favorites = self.load_favorites()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Quick Access Combo Box
        self.quick_access = QComboBox()
        self.setup_quick_access()
        layout.addWidget(self.quick_access)
        
        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search images...")
        self.search_timer = QTimer()  # For search delay
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.perform_search)
        self.search_bar.textChanged.connect(self.search_text_changed)
        layout.addWidget(self.search_bar)
        
        # Create file system model
        self.file_system = QFileSystemModel()
        
        # Verify the path exists, fall back to home directory if it doesn't
        if not os.path.exists(self.start_path):
            self.start_path = QDir.homePath()
            print(f"Warning: Specified path not found, falling back to: {self.start_path}")
        
        # Set the starting directory
        self.file_system.setRootPath(self.start_path)
        
        # Create tree view
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_system)
        self.tree_view.setRootIndex(self.file_system.index(self.start_path))
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        
        # Configure view
        self.tree_view.setColumnWidth(0, 200)
        self.tree_view.hideColumn(1)
        self.tree_view.hideColumn(2)
        self.tree_view.hideColumn(3)
        
        # Set name filters for image files
        self.file_system.setNameFilters(['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif'])
        self.file_system.setNameFilterDisables(False)
        
        # Connect selection signal
        self.tree_view.clicked.connect(self.on_file_selected)
        
        layout.addWidget(self.tree_view)
        
        # Favorites Section
        favorites_label = QLabel("Favorites")
        layout.addWidget(favorites_label)
        
        self.favorites_combo = QComboBox()
        self.update_favorites_combo()
        self.favorites_combo.currentIndexChanged.connect(self.favorite_selected)
        layout.addWidget(self.favorites_combo)
        
    def setup_quick_access(self):
        """Setup quick access locations"""
        common_paths = [
            ("Pictures", QDir.homePath() + "/Pictures"),
            ("Documents", QDir.homePath() + "/Documents"),
            ("Downloads", QDir.homePath() + "/Downloads"),
            ("Desktop", QDir.homePath() + "/Desktop"),
            ("OneDrive Pictures", r"C:\Users\colca\OneDrive\Pictures"),
        ]
        
        self.quick_access.addItem("Quick Access Locations...")
        for name, path in common_paths:
            if os.path.exists(path):
                self.quick_access.addItem(name, path)
                
        self.quick_access.currentIndexChanged.connect(self.quick_access_changed)
        
    def quick_access_changed(self, index):
        if index > 0:  # 0 is the placeholder text
            path = self.quick_access.currentData()
            self.tree_view.setRootIndex(self.file_system.index(path))
            
    def search_text_changed(self):
        """Start timer for search delay"""
        self.search_timer.start(300)  # 300ms delay
        
    def perform_search(self):
        """Perform the actual search"""
        search_text = self.search_bar.text().lower()
        if not search_text:
            # Reset to normal view
            self.file_system.setNameFilters(['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.gif'])
            return
            
        # Add search term to name filters
        self.file_system.setNameFilters([f'*{search_text}*.jpg', f'*{search_text}*.jpeg',
                                       f'*{search_text}*.png', f'*{search_text}*.bmp',
                                       f'*{search_text}*.gif'])
        
    def show_context_menu(self, position):
        """Show context menu for adding/removing favorites"""
        index = self.tree_view.indexAt(position)
        if index.isValid():
            path = self.file_system.filePath(index)
            if os.path.isdir(path):  # Only show for directories
                menu = QMenu()
                if path in self.favorites:
                    remove_action = QAction("Remove from Favorites", self)
                    remove_action.triggered.connect(lambda: self.remove_favorite(path))
                    menu.addAction(remove_action)
                else:
                    add_action = QAction("Add to Favorites", self)
                    add_action.triggered.connect(lambda: self.add_favorite(path))
                    menu.addAction(add_action)
                menu.exec(self.tree_view.viewport().mapToGlobal(position))
                
    def load_favorites(self):
        """Load favorites from file"""
        try:
            with open('favorites.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
            
    def save_favorites(self):
        """Save favorites to file"""
        with open('favorites.json', 'w') as f:
            json.dump(self.favorites, f)
            
    def update_favorites_combo(self):
        """Update favorites combo box"""
        self.favorites_combo.clear()
        self.favorites_combo.addItem("Favorite Locations...")
        for path in self.favorites:
            self.favorites_combo.addItem(os.path.basename(path), path)
            
    def add_favorite(self, path):
        """Add a path to favorites"""
        if path not in self.favorites:
            self.favorites.append(path)
            self.save_favorites()
            self.update_favorites_combo()
            QMessageBox.information(self, "Success", "Location added to favorites!")
            
    def remove_favorite(self, path):
        """Remove a path from favorites"""
        if path in self.favorites:
            self.favorites.remove(path)
            self.save_favorites()
            self.update_favorites_combo()
            QMessageBox.information(self, "Success", "Location removed from favorites!")
            
    def favorite_selected(self, index):
        """Handle favorite location selection"""
        if index > 0:  # 0 is the placeholder text
            path = self.favorites_combo.currentData()
            if os.path.exists(path):
                self.tree_view.setRootIndex(self.file_system.index(path))
            else:
                QMessageBox.warning(self, "Error", "Selected location no longer exists!")
                self.remove_favorite(path)
                
    def on_file_selected(self, index):
        file_path = self.file_system.filePath(index)
        self.file_selected.emit(file_path)

class DropIndicatorOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Semi-transparent blue color
        color = QColor(0, 120, 215, 128)
        painter.setBrush(color)
        painter.setPen(QPen(color.darker(), 2))
        
        # Draw rounded rectangle
        painter.drawRoundedRect(self.rect(), 10, 10)

class DropZoneOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.zone_type = None  # 'top', 'bottom', or 'middle'
        self.active = False
        self.hide()

    def paintEvent(self, event):
        if not self.active:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Semi-transparent blue for inactive, more opaque for active
        color = QColor(0, 120, 215, 100)
        border_color = QColor(0, 120, 215, 255)

        # Draw the drop zone
        painter.setBrush(color)
        painter.setPen(QPen(border_color, 2, Qt.DashLine))
        painter.drawRoundedRect(self.rect(), 10, 10)

        # Draw an icon or text indicating the layout
        painter.setPen(QPen(border_color, 2, Qt.SolidLine))
        center_x = self.width() // 2
        center_y = self.height() // 2

        if self.zone_type == 'top':
            # Draw up arrow and "Drop to move to top" text
            text = "Drop here for vertical layout (top)"
            painter.drawText(self.rect(), Qt.AlignCenter, text)
        elif self.zone_type == 'bottom':
            # Draw down arrow and "Drop to move to bottom" text
            text = "Drop here for vertical layout (bottom)"
            painter.drawText(self.rect(), Qt.AlignCenter, text)
        elif self.zone_type == 'middle':
            # Draw horizontal arrows and "Drop for side-by-side" text
            text = "Drop here for horizontal layout"
            painter.drawText(self.rect(), Qt.AlignCenter, text)

class ProcessingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.hide()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Create progress bar
        self.progress = QProgressBar()
        self.progress.setMinimum(0)
        self.progress.setMaximum(0)  # Indeterminate progress
        self.progress.setFixedWidth(200)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 2px solid #ccc;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0078d4;
                border-radius: 3px;
            }
        """)

        # Create status label
        self.status_label = QLabel("Processing...")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font-weight: bold;
                background-color: rgba(255, 255, 255, 220);
                padding: 5px;
                border-radius: 3px;
            }
        """)

        layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.progress, alignment=Qt.AlignCenter)

    def set_status(self, text):
        self.status_label.setText(text)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 255, 200))

class DraggableImageLabel(QLabel):
    dragStarted = Signal(QPoint)
    dropped = Signal(QPoint)
    
    def __init__(self, title: str):
        super().__init__(title)
        self.setMinimumSize(200, 200)
        self.setAlignment(Qt.AlignCenter)
        self.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.setAcceptDrops(True)
        self.drag_start_position = None
        self.original_pixmap = None
        self.is_dragging = False  # Initialize is_dragging attribute

        self.setStyleSheet("""
            DraggableImageLabel {
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            DraggableImageLabel:hover {
                border-color: #0078d4;
            }
        """)
        
        self.setScaledContents(False)  # We'll handle scaling manually

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            self.is_dragging = False  # Reset dragging state

    def mouseMoveEvent(self, event: QMouseEvent):
        if not (event.buttons() & Qt.LeftButton):
            return
        if not self.drag_start_position:
            return
        
        if not self.is_dragging and (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return

        self.is_dragging = True
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.objectName())
        drag.setMimeData(mime_data)

        pixmap = self.grab()
        painter = QPainter(pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QColor(0, 0, 0, 127))
        painter.end()
        
        drag.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        drag.setHotSpot(event.pos())
        
        self.dragStarted.emit(event.globalPos())
        drag.exec_(Qt.MoveAction)
        
        self.is_dragging = False
        self.setCursor(Qt.ArrowCursor)

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()
            self.setStyleSheet("""
                DraggableImageLabel {
                    border: 2px solid #0078d4;
                    border-radius: 5px;
                    background-color: #f0f8ff;
                }
            """)

    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            DraggableImageLabel {
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            DraggableImageLabel:hover {
                border-color: #0078d4;
            }
        """)

    def dropEvent(self, event):
        self.dropped.emit(event.pos())
        event.acceptProposedAction()
        self.setStyleSheet("""
            DraggableImageLabel {
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            DraggableImageLabel:hover {
                border-color: #0078d4;
            }
        """)

class ImageViewerContainer(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize state variables first
        self.is_dragging = False
        self.drag_source = None
        self.current_layout = "horizontal"
        self.init_ui()
        
    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main splitter
        self.splitter = QSplitter(Qt.Horizontal)
        
        # Create image labels
        self.original_label = DraggableImageLabel("Original Image")
        self.original_label.setObjectName("original")
        self.edited_label = DraggableImageLabel("Edited Image")
        self.edited_label.setObjectName("edited")
        
        # Create processing overlay
        self.processing_overlay = ProcessingOverlay(self)
        self.processing_overlay.hide()

        # Create drop zones
        self.top_zone = DropZoneOverlay(self)
        self.top_zone.zone_type = 'top'
        self.middle_zone = DropZoneOverlay(self)
        self.middle_zone.zone_type = 'middle'
        self.bottom_zone = DropZoneOverlay(self)
        self.bottom_zone.zone_type = 'bottom'
        
        # Connect drag and drop signals
        self.original_label.dragStarted.connect(self.handle_drag_start)
        self.original_label.dropped.connect(self.handle_drop)
        self.edited_label.dragStarted.connect(self.handle_drag_start)
        self.edited_label.dropped.connect(self.handle_drop)
        
        # Add labels to splitter
        self.splitter.addWidget(self.original_label)
        self.splitter.addWidget(self.edited_label)
        
        # Set splitter properties
        self.splitter.setHandleWidth(8)
        self.splitter.setChildrenCollapsible(False)
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e1e1e1;
                border: 1px solid #c1c1c1;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
        """)
        
        self.main_layout.addWidget(self.splitter)
        
        # Initialize drop zones hidden
        self.update_drop_zones()
    
    def update_drop_zones(self):
        """Update the position and size of drop zones"""
        if not self.is_dragging:
            self.top_zone.hide()
            self.middle_zone.hide()
            self.bottom_zone.hide()
            return

        # Calculate zones
        height = self.height()
        width = self.width()
        zone_height = height // 3

        # Top zone
        self.top_zone.setGeometry(0, 0, width, zone_height)
        self.top_zone.show()
        self.top_zone.active = True

        # Middle zone
        self.middle_zone.setGeometry(0, zone_height, width, zone_height)
        self.middle_zone.show()
        self.middle_zone.active = True

        # Bottom zone
        self.bottom_zone.setGeometry(0, zone_height * 2, width, zone_height)
        self.bottom_zone.show()
        self.bottom_zone.active = True

    def handle_drag_start(self, pos):
        self.drag_source = self.sender()
        self.is_dragging = True
        self.update_drop_zones()

    def update_drop_indicators(self, pos):
        if not hasattr(self, 'vertical_indicator'):
            return

        # Get the widget's geometry
        rect = self.rect()
        
        # Configure vertical drop zones (top and bottom halves)
        top_height = rect.height() // 3
        bottom_y = rect.height() * 2 // 3
        
        # Show/hide indicators based on mouse position
        local_pos = self.mapFromGlobal(pos)
        
        # Update vertical indicator
        if local_pos.y() < top_height:
            self.vertical_indicator.setGeometry(0, 0, rect.width(), rect.height() // 2)
            self.vertical_indicator.show()
            self.horizontal_indicator.hide()
        elif local_pos.y() > bottom_y:
            self.vertical_indicator.setGeometry(0, rect.height() // 2, 
                                              rect.width(), rect.height() // 2)
            self.vertical_indicator.show()
            self.horizontal_indicator.hide()
        else:
            # Show horizontal indicator in the middle zone
            self.horizontal_indicator.setGeometry(0, 0, rect.width(), rect.height())
            self.horizontal_indicator.show()
            self.vertical_indicator.hide()

    def handle_drag_enter(self, event):
        event.accept()

    def handle_drop(self, pos):
        self.is_dragging = False
        drop_target = self.sender()
        
        if self.drag_source and drop_target and self.drag_source != drop_target:
            # Convert position to local coordinates
            local_pos = self.mapFromGlobal(pos)
            zone_height = self.height() // 3

            # Determine which zone received the drop
            if local_pos.y() < zone_height:
                # Top zone - vertical layout with dropped item on top
                self.set_layout("vertical", self.drag_source.objectName() == "edited")
            elif local_pos.y() < zone_height * 2:
                # Middle zone - horizontal layout
                self.set_layout("horizontal", self.drag_source.objectName() == "edited")
            else:
                # Bottom zone - vertical layout with dropped item on bottom
                self.set_layout("vertical", self.drag_source.objectName() != "edited")

        # Hide drop zones
        self.update_drop_zones()


    def set_layout(self, layout_type, swap_order=False):
        """Set the layout and optionally swap the order of widgets"""
        if layout_type != self.current_layout or swap_order:
            self.current_layout = layout_type
            
            # Remove widgets from splitter
            self.original_label.setParent(None)
            self.edited_label.setParent(None)
            
            # Create new splitter with correct orientation
            old_splitter = self.splitter
            self.splitter = QSplitter(
                Qt.Vertical if layout_type == "vertical" else Qt.Horizontal
            )
            self.splitter.setHandleWidth(8)
            self.splitter.setChildrenCollapsible(False)
            
            # Add widgets back in the correct order
            if not swap_order:
                self.splitter.addWidget(self.original_label)
                self.splitter.addWidget(self.edited_label)
            else:
                self.splitter.addWidget(self.edited_label)
                self.splitter.addWidget(self.original_label)
            
            # Replace old splitter with new one
            self.main_layout.replaceWidget(old_splitter, self.splitter)
            old_splitter.deleteLater()
            
            # Set equal sizes
            total_size = (self.height() if layout_type == "vertical" else self.width())
            self.splitter.setSizes([total_size // 2, total_size // 2])

    def update_images(self, original_image: QImage, edited_image: QImage):
        # Convert QImage to QPixmap for better display
        original_pixmap = QPixmap.fromImage(original_image)
        edited_pixmap = QPixmap.fromImage(edited_image)
        
        # Set the pixmaps (scaling will be handled by DraggableImageLabel)
        self.original_label.setPixmap(original_pixmap)
        self.edited_label.setPixmap(edited_pixmap)
        
    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'processing_overlay'):
            self.processing_overlay.setGeometry(self.rect())
        if self.is_dragging:
            self.update_drop_zones()
            
    def show_processing(self, message="Processing..."):
        self.processing_overlay.set_status(message)
        self.processing_overlay.setGeometry(self.rect())
        self.processing_overlay.show()
        QApplication.processEvents()  # Ensure UI updates

    def hide_processing(self):
        self.processing_overlay.hide()



class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.processor = ImageProcessor()
        
    def apply_processing(self, operation, *args, **kwargs):
        """Generic method to apply image processing operations with overlay"""
        if self.processor.has_image():
            self.container.show_processing(f"Applying {operation}...")
            try:
                # Get the processing method from the processor
                processing_method = getattr(self.processor, operation)
                # Apply the processing
                processing_method(*args, **kwargs)
                # Update the display
                self.update_display()
            finally:
                self.container.hide_processing()

    def update_display(self):
        if self.processor.has_image():
            original_qt = self.processor.get_qt_image(self.processor.current_image)
            edited_qt = self.processor.get_qt_image(self.processor.edited_image)
            self.container.update_images(original_qt, edited_qt)

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.container = ImageViewerContainer()
        layout.addWidget(self.container)
        
    def load_image(self, file_path):
        self.processor.load_image(file_path)
        self.update_display()
        
    def update_display(self):
        if self.processor.has_image():
            original_qt = self.processor.get_qt_image(self.processor.current_image)
            edited_qt = self.processor.get_qt_image(self.processor.edited_image)
            self.container.update_images(original_qt, edited_qt)

class ParameterSlider(QWidget):
    """Custom slider widget with label and value display"""
    valueChanged = Signal(float)
    
    def __init__(self, label, min_val, max_val, default_val, step=0.1):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Label
        self.label = QLabel(label)
        self.label.setMinimumWidth(100)
        
        # Slider
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(int(min_val / step))
        self.slider.setMaximum(int(max_val / step))
        self.slider.setValue(int(default_val / step))
        
        # Value display
        self.value_label = QLabel(f"{default_val:.1f}")
        self.value_label.setMinimumWidth(40)
        
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.value_label)
        
        # Connect slider
        self.step = step
        self.slider.valueChanged.connect(self._on_slider_changed)
        
    def _on_slider_changed(self, value):
        actual_value = value * self.step
        self.value_label.setText(f"{actual_value:.1f}")
        self.valueChanged.emit(actual_value)
        
    def value(self):
        return self.slider.value() * self.step
    
# Keep only this version and remove the other two duplicate class definitions:
class SegmentationDialog(QDialog):
    """Dialog for adjusting segmentation parameters with presets"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Segmentation Parameters")
        self.setModal(True)
        
        # Define presets
        self.presets = {
            "Custom": SegmentationParams(),  # Default parameters
            "Cartoon": SegmentationParams(
                n_segments=100,
                n_colors=8,
                compactness=20,
                edge_weight=1.0,
                edge_enhancement=0.8,
                smoothing_factor=0.7
            ),
            "Painterly": SegmentationParams(
                n_segments=200,
                n_colors=12,
                compactness=5,
                edge_weight=0.3,
                edge_enhancement=0.2,
                smoothing_factor=0.6
            ),
            "Abstract": SegmentationParams(
                n_segments=50,
                n_colors=6,
                compactness=30,
                edge_weight=0.5,
                edge_enhancement=0.4,
                smoothing_factor=0.8
            )
        }
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Preset selection
        preset_layout = QHBoxLayout()
        preset_label = QLabel("Preset:")
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(list(self.presets.keys()))
        self.preset_combo.currentTextChanged.connect(self.apply_preset)
        preset_layout.addWidget(preset_label)
        preset_layout.addWidget(self.preset_combo)
        layout.addLayout(preset_layout)
        
        # Add separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Parameter controls group
        params_group = QGroupBox("Parameters")
        params_layout = QVBoxLayout()
        
        # Create sliders
        self.n_segments = ParameterSlider("Segments", 10, 500, 100, 10)
        self.n_colors = ParameterSlider("Colors", 2, 32, 8, 1)
        self.compactness = ParameterSlider("Compactness", 1, 100, 10, 1)
        self.sigma = ParameterSlider("Smoothing", 0, 10, 3, 0.1)
        self.edge_weight = ParameterSlider("Edge Weight", 0, 1, 0.5, 0.1)
        self.smoothing_factor = ParameterSlider("Final Smoothing", 0, 1, 0.5, 0.1)
        self.edge_enhancement = ParameterSlider("Edge Enhancement", 0, 1, 0.5, 0.1)
        
        # Add all sliders to the parameters group
        params_layout.addWidget(self.n_segments)
        params_layout.addWidget(self.n_colors)
        params_layout.addWidget(self.compactness)
        params_layout.addWidget(self.sigma)
        params_layout.addWidget(self.edge_weight)
        params_layout.addWidget(self.smoothing_factor)
        params_layout.addWidget(self.edge_enhancement)
        
        # Color space selection
        color_space_layout = QHBoxLayout()
        color_space_label = QLabel("Color Space")
        self.color_space = QComboBox()
        self.color_space.addItems(['lab', 'rgb', 'hsv'])
        color_space_layout.addWidget(color_space_label)
        color_space_layout.addWidget(self.color_space)
        params_layout.addLayout(color_space_layout)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Add separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # Buttons
        buttons = QHBoxLayout()
        self.apply_btn = QPushButton("Apply")
        self.cancel_btn = QPushButton("Cancel")
        buttons.addWidget(self.apply_btn)
        buttons.addWidget(self.cancel_btn)
        layout.addLayout(buttons)
        
        # Connect buttons
        self.apply_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        # Connect slider signals to update preset to "Custom" when changed
        for slider in [self.n_segments, self.n_colors, self.compactness,
                      self.sigma, self.edge_weight, self.smoothing_factor,
                      self.edge_enhancement]:
            slider.valueChanged.connect(self.on_parameter_changed)
        
        self.color_space.currentTextChanged.connect(self.on_parameter_changed)
        
        # Set initial preset
        self.apply_preset("Custom")
        
    def apply_preset(self, preset_name):
        """Apply the selected preset to all controls"""
        if preset_name not in self.presets:
            return
            
        params = self.presets[preset_name]
        
        # Update all controls
        self.n_segments.slider.setValue(int(params.n_segments / self.n_segments.step))
        self.n_colors.slider.setValue(int(params.n_colors / self.n_colors.step))
        self.compactness.slider.setValue(int(params.compactness / self.compactness.step))
        self.sigma.slider.setValue(int(params.sigma / self.sigma.step))
        self.edge_weight.slider.setValue(int(params.edge_weight / self.edge_weight.step))
        self.smoothing_factor.slider.setValue(int(params.smoothing_factor / self.smoothing_factor.step))
        self.edge_enhancement.slider.setValue(int(params.edge_enhancement / self.edge_enhancement.step))
        
        # Set color space
        index = self.color_space.findText(params.color_space)
        if index >= 0:
            self.color_space.setCurrentIndex(index)
            
    def on_parameter_changed(self, *args):
        """When any parameter is changed, switch to Custom preset"""
        if self.preset_combo.currentText() != "Custom":
            self.preset_combo.setCurrentText("Custom")
    
    def get_parameters(self):
        """Return the current parameters as a SegmentationParams object"""
        return SegmentationParams(
            n_segments=int(self.n_segments.value()),
            n_colors=int(self.n_colors.value()),
            compactness=self.compactness.value(),
            sigma=self.sigma.value(),
            edge_weight=self.edge_weight.value(),
            color_space=self.color_space.currentText(),
            smoothing_factor=self.smoothing_factor.value(),
            edge_enhancement=self.edge_enhancement.value()
        )

class ToolPanel(QWidget):
    def __init__(self, image_viewer):
        super().__init__()
        self.image_viewer = image_viewer
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Create buttons
        self.grayscale_btn = QPushButton("Grayscale")
        self.kmeans_btn = QPushButton("K-means")
        self.segment_btn = QPushButton("Smart Segmentation")
        self.save_btn = QPushButton("Save")
        
        # Add buttons to layout
        layout.addWidget(self.grayscale_btn)
        layout.addWidget(self.kmeans_btn)
        layout.addWidget(self.segment_btn)
        layout.addWidget(self.save_btn)
        
        # Connect buttons to functions
        self.grayscale_btn.clicked.connect(self.apply_grayscale)
        self.kmeans_btn.clicked.connect(self.apply_kmeans)
        self.segment_btn.clicked.connect(self.apply_segmentation)
        self.save_btn.clicked.connect(self.save_image)
        
        # Add stretch to push buttons to top
        layout.addStretch()
        
    def apply_segmentation(self):
        dialog = SegmentationDialog(self)
        if dialog.exec() == QDialog.Accepted:
            params = dialog.get_parameters()
            self.image_viewer.apply_processing('apply_smooth_segmentation', params)
        
    def apply_grayscale(self):
        self.image_viewer.apply_processing('apply_grayscale')
        
    def apply_kmeans(self):
        k, ok = QInputDialog.getInt(
            self, "K-means Clustering", 
            "Enter number of clusters (2-16):", 8, 2, 16, 1)
        if ok:
            self.image_viewer.apply_processing('apply_kmeans', k)
            
    def save_image(self):
        if self.image_viewer.processor.has_image():
            file_name, _ = QFileDialog.getSaveFileName(
                self, "Save Image", "", 
                "Images (*.png *.jpg *.jpeg *.bmp)")
            if file_name:
                self.image_viewer.container.show_processing("Saving image...")
                try:
                    self.image_viewer.processor.save_image(file_name)
                finally:
                    self.image_viewer.container.hide_processing()
