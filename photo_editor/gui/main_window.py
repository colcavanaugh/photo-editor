# photo_editor/gui/main_window.py
from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QSplitter
from PySide6.QtCore import Qt
from photo_editor.gui.widgets import FileNavigator, ImageViewer, ToolPanel

class PhotoEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Photo Editor")
        self.setGeometry(100, 100, 1200, 800)
        
        # Main widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)  # Remove spacing between widgets
        
        # Create main horizontal splitter
        self.h_splitter = QSplitter(Qt.Horizontal)
        
        # Create components
        self.file_navigator = FileNavigator(r"C:\Users\colca\OneDrive\Pictures")
        self.image_viewer = ImageViewer()
        self.tool_panel = ToolPanel(self.image_viewer)
        
        # Set minimum and maximum sizes for file navigator
        self.file_navigator.setMinimumWidth(100)
        self.file_navigator.setMaximumWidth(400)
        
        # Set minimum sizes for tool panel
        self.tool_panel.setMinimumWidth(150)
        self.tool_panel.setMaximumWidth(300)
        
        # Add components to splitters
        self.h_splitter.addWidget(self.file_navigator)
        self.h_splitter.addWidget(self.image_viewer)
        self.h_splitter.addWidget(self.tool_panel)
        
        # Style the splitter
        self.h_splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #e1e1e1;
                border: 1px solid #c1c1c1;
                border-radius: 2px;
                margin: 2px;
            }
            QSplitter::handle:hover {
                background-color: #0078d4;
            }
            QSplitter::handle:pressed {
                background-color: #005a9e;
            }
        """)
        
        # Set handle width
        self.h_splitter.setHandleWidth(8)
        
        # Set initial sizes (proportions of the total width)
        total_width = 1200  # This matches our initial window width
        self.h_splitter.setSizes([
            int(total_width * 0.2),  # 20% for file navigator
            int(total_width * 0.6),  # 60% for image viewer
            int(total_width * 0.2)   # 20% for tool panel
        ])
        
        # Add the main splitter to the layout
        main_layout.addWidget(self.h_splitter)
        
        # Connect file navigator to image viewer
        self.file_navigator.file_selected.connect(self.image_viewer.load_image)
        
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Maintain proportions on window resize
        if hasattr(self, 'h_splitter'):
            total_width = event.size().width()
            current_sizes = self.h_splitter.sizes()
            total_current = sum(current_sizes)
            if total_current > 0:  # Avoid division by zero
                # Maintain the current proportions
                new_sizes = [
                    int(size * total_width / total_current)
                    for size in current_sizes
                ]
                self.h_splitter.setSizes(new_sizes)