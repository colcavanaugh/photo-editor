import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage
from photo_editor.gui.main_window import MainWindow

@pytest.fixture
def app(qapp):
    """Provides Qt Application instance.
    qapp fixture comes from pytest-qt"""
    return qapp

@pytest.fixture
def main_window(app):
    """Provides the main window instance for testing"""
    window =MainWindow()
    window.show()
    return window

def test_window_creation(main_window):
    """Test that window is created with correct initial state.
    
    Rationale: Ensures our most basic functionality - creating and showing
    a window - workfs correctly. This is our "hello world" test.
    """

    assert main_window is not None
    assert main_window.windowTitle() == "Photo Editor"
    assert main_window.isVisible()

def test_initial_image_display_state(main_window):
    """Test that image display area exists and starts empty.
    
    Rationale: Before loading any images, we should have a properly
    initialized by empty display area. This prevents undefined behavior
    when the app starts.
    """

    assert main_window.image_display is not None
    assert main_window.image_display.pixmap() is None

def test_file_menu_exists(main_window):
    """Test that basic file menu is present with required actions.
    
    Rationale: Users need basic file operations (open/save) for MVP.
    This ensures the menu structure exists before we implement actions.
    """

    menubar = main_window.menuBar()
    file_menu = menubar.findChild(QMenu, "file_menu")
    assert file_menu is not None

    # Check for essential actions
    open_action = file_menu.findChild(QAction, "open_action")
    save_action = file_menu.findChild(QAction, "save_action")
    assert open_action is not None
    assert save_action is not None

def test_grayscale_button_exists(main_window):
    """Test that grayscale conversion button exists and starts disabled.
    
    Rationale: Our MVP includes grayscale conversion. Button should exist
    but be disabled until an image is loaded.
    """

    grayscale_button = main_window.findChild(QPushButton, "grayscale_button")
    assert grayscale_button is not None
    assert not grayscale_button.isEnabled()

    