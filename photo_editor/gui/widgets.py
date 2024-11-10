import os
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QTreeView, QInputDialog, QFileDialog,
                            QFileSystemModel, QComboBox, QLineEdit, QMenu,
                            QMessageBox, QSplitter, QFrame, QApplication,
                            QProgressBar, QDialog, QSlider, QGroupBox)
from PySide6.QtCore import Qt, QDir, Signal, QTimer, QPoint, QRect, QSize, QMimeData, QEvent
from PySide6.QtGui import (QPixmap, QImage, QAction, QDrag, QMouseEvent, 
                          QPainter, QColor, QPen, QPainterPath, QCursor, QFont)
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

class DropZoneOverlay(QWidget):
    """A simplified overlay widget that shows two drop zones."""
    
    zoneEntered = Signal(str)  # Emits zone name when entered
    zoneDropped = Signal(str)  # Emits zone name when dropped
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint)  # Removed Qt.Tool flag
        self.zones = {}
        self.active_zone = None
        self.orientation = "horizontal"  # or "vertical"
        
    def show_zones(self, orientation="horizontal"):
        """Show the drop zones with specified orientation."""
        self.orientation = orientation
        self.update_zones()
        self.show()
        self.raise_()
        
    def hide_zones(self):
        """Hide the drop zones."""
        self.hide()
        self.active_zone = None
        
    def update_zones(self):
        """Update the zones' geometry based on orientation."""
        margin = 20  # Margin from edges
        zone_alpha = 40  # Base transparency (0-255)
        active_alpha = 80  # Hover transparency (0-255)
        
        if self.orientation == "horizontal":
            # Left and Right zones
            left_zone = QRect(
                margin,
                margin,
                (self.width() - margin * 3) // 2,
                self.height() - margin * 2
            )
            right_zone = QRect(
                self.width() // 2 + margin // 2,
                margin,
                (self.width() - margin * 3) // 2,
                self.height() - margin * 2
            )
            self.zones = {
                "left": {"rect": left_zone, "alpha": zone_alpha},
                "right": {"rect": right_zone, "alpha": zone_alpha}
            }
        else:
            # Top and Bottom zones
            top_zone = QRect(
                margin,
                margin,
                self.width() - margin * 2,
                (self.height() - margin * 3) // 2
            )
            bottom_zone = QRect(
                margin,
                self.height() // 2 + margin // 2,
                self.width() - margin * 2,
                (self.height() - margin * 3) // 2
            )
            self.zones = {
                "top": {"rect": top_zone, "alpha": zone_alpha},
                "bottom": {"rect": bottom_zone, "alpha": zone_alpha}
            }
            
        # Update active zone's alpha if it exists
        if self.active_zone and self.active_zone in self.zones:
            self.zones[self.active_zone]["alpha"] = active_alpha
            
    def paintEvent(self, event):
        """Paint the drop zones."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        for zone_name, zone_info in self.zones.items():
            rect = zone_info["rect"]
            alpha = zone_info["alpha"]
            
            # Draw semi-transparent blue rectangle
            color = QColor(0, 120, 215, alpha)
            painter.fillRect(rect, color)
            
            # Draw border
            border_color = QColor(0, 120, 215, 255)
            painter.setPen(QPen(border_color, 2, Qt.DashLine))
            painter.drawRect(rect)
            
            # Draw text
            text_color = QColor(0, 0, 0, 255 if self.active_zone == zone_name else 180)
            painter.setPen(QPen(text_color))
            text = f"Drop to move {zone_name}"
            painter.setFont(QFont("Arial", 10, QFont.Bold))
            painter.drawText(rect, Qt.AlignCenter, text)
            
    def get_zone_at(self, pos):
        """Return the zone name at the given position."""
        for zone_name, zone_info in self.zones.items():
            if zone_info["rect"].contains(pos):
                return zone_name
        return None
        
    def update_active_zone(self, pos):
        """Update the active zone based on cursor position."""
        new_zone = self.get_zone_at(pos)
        if new_zone != self.active_zone:
            self.active_zone = new_zone
            self.zoneEntered.emit(new_zone if new_zone else "")
            self.update_zones()
            self.update()

class DraggableImageLabel(QLabel):
    """Main image display label that can be dragged."""
    def __init__(self, title: str):
        super().__init__(title)
        self.setMinimumSize(200, 200)
        self.setAlignment(Qt.AlignCenter)
        self.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.setAcceptDrops(True)
        
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            QLabel:hover {
                border-color: #0078d4;
            }
        """)
        
        self.setScaledContents(False)

class DragPreviewWidget(QWidget):
    """Widget showing a semi-transparent preview during drag."""
    def __init__(self, pixmap, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        
        # Scale the pixmap for the drag preview
        scaled_size = QSize(200, 200)
        self.preview = pixmap.scaled(scaled_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        
        # Set widget size
        self.setFixedSize(self.preview.size())
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw semi-transparent image
        painter.setOpacity(0.7)
        painter.drawPixmap(0, 0, self.preview)

class ImageViewerContainer(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.is_dragging = False
        self.current_layout = "horizontal"
        self.drag_source = None
        self.drag_preview = None
        self.drag_start_pos = None
        
    def init_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter and image labels
        self.splitter = QSplitter(Qt.Horizontal)
        self.original_label = DraggableImageLabel("Original Image")
        self.edited_label = DraggableImageLabel("Edited Image")
        
        self.splitter.addWidget(self.original_label)
        self.splitter.addWidget(self.edited_label)
        
        # Set up overlay
        self.drop_overlay = DropZoneOverlay(self)
        self.drop_overlay.zoneEntered.connect(self.on_zone_entered)
        self.drop_overlay.zoneDropped.connect(self.on_zone_dropped)
        
        # Connect mouse events
        for label in [self.original_label, self.edited_label]:
            label.installEventFilter(self)
        
        self.layout.addWidget(self.splitter)
        
    def on_zone_entered(self, zone_name):
        """Handle when the drag enters a drop zone."""
        if zone_name and self.is_dragging:
            self.drop_overlay.active_zone = zone_name
            self.drop_overlay.update()
            
    def on_zone_dropped(self, zone_name):
        """Handle when the image is dropped in a zone."""
        if not zone_name:
            return
            
        # Update layout based on drop zone
        if zone_name in ["left", "right"]:
            self.current_layout = "horizontal"
            self.set_layout("horizontal", zone_name == "right")
        else:
            self.current_layout = "vertical"
            self.set_layout("vertical", zone_name == "bottom")
            
        self.drop_overlay.hide_zones()
        self.is_dragging = False
        
    def eventFilter(self, obj, event):
        """Handle mouse events for the image labels."""
        if obj in [self.original_label, self.edited_label]:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                return self.start_drag(event, obj)
            elif event.type() == QEvent.MouseMove and self.is_dragging:
                return self.update_drag(event)
            elif event.type() == QEvent.MouseButtonRelease and self.is_dragging:
                return self.end_drag(event)
        return super().eventFilter(obj, event)
    
    def start_drag(self, event, source):
        """Handle the start of a drag operation."""
        if not source.pixmap():
            return False
            
        self.is_dragging = True
        self.drag_source = source
        self.drag_start_pos = event.pos()
        
        # Create and show drag preview
        preview_pixmap = source.pixmap()
        self.drag_preview = DragPreviewWidget(preview_pixmap)
        
        # Position preview at cursor
        global_pos = source.mapToGlobal(event.pos())
        self.drag_preview.move(global_pos - QPoint(self.drag_preview.width()//2, 
                                                  self.drag_preview.height()//2))
        self.drag_preview.show()
        
        # Show drop zones
        self.drop_overlay.setGeometry(self.rect())
        self.drop_overlay.show_zones(
            "vertical" if self.current_layout == "horizontal" else "horizontal"
        )
        
        return True
        
    def update_drag(self, event):
        """Update drag preview and drop zone highlighting."""
        if self.drag_preview and self.is_dragging:
            # Update preview position
            global_pos = self.drag_source.mapToGlobal(event.pos())
            self.drag_preview.move(global_pos - QPoint(self.drag_preview.width()//2, 
                                                     self.drag_preview.height()//2))
            
            # Update active drop zone
            local_pos = self.mapFromGlobal(global_pos)
            self.drop_overlay.update_active_zone(local_pos)
        
        return True
        
    def end_drag(self, event):
        """Handle the end of a drag operation."""
        if self.drag_preview:
            self.drag_preview.hide()
            self.drag_preview.deleteLater()
            self.drag_preview = None
            
        if self.is_dragging:
            global_pos = self.drag_source.mapToGlobal(event.pos())
            local_pos = self.mapFromGlobal(global_pos)
            zone = self.drop_overlay.get_zone_at(local_pos)
            
            if zone:
                self.on_zone_dropped(zone)
                
            self.drop_overlay.hide_zones()
            self.is_dragging = False
        
        return True
    
    def set_layout(self, layout_type, swap_order=False):
        """Update the splitter layout."""
        # Remove widgets from splitter
        self.original_label.setParent(None)
        self.edited_label.setParent(None)
        
        # Create new splitter with correct orientation
        old_splitter = self.splitter
        self.splitter = QSplitter(
            Qt.Vertical if layout_type == "vertical" else Qt.Horizontal
        )
        
        # Add widgets back in the correct order
        if not swap_order:
            self.splitter.addWidget(self.original_label)
            self.splitter.addWidget(self.edited_label)
        else:
            self.splitter.addWidget(self.edited_label)
            self.splitter.addWidget(self.original_label)
        
        # Replace old splitter
        self.layout.replaceWidget(old_splitter, self.splitter)
        old_splitter.deleteLater()
        
        # Set equal sizes
        total_size = (self.height() if layout_type == "vertical" else self.width())
        self.splitter.setSizes([total_size // 2, total_size // 2])

    def resizeEvent(self, event):
        """Handle container resize."""
        super().resizeEvent(event)
        if self.is_dragging:
            self.drop_overlay.setGeometry(self.rect())
            self.drop_overlay.update_zones()

    def update_images(self, original_image: QImage, edited_image: QImage):
        """Update the displayed images."""
        # Convert QImage to QPixmap for better display
        original_pixmap = QPixmap.fromImage(original_image)
        edited_pixmap = QPixmap.fromImage(edited_image)
        
        # Set the pixmaps
        self.original_label.setPixmap(original_pixmap)
        self.edited_label.setPixmap(edited_pixmap)

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
