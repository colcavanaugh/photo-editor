# photo_editor/main.py
import sys
from PySide6.QtWidgets import QApplication
from photo_editor.gui.main_window import PhotoEditorWindow

def main():
    app = QApplication(sys.argv)
    window = PhotoEditorWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()