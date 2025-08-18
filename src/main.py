import sys
from PySide6.QtWidgets import QApplication
from ui.main_window import VideoLocalizerApp


def main():
    app = QApplication(sys.argv)

    # Настройка стилей
    app.setStyle("Fusion")

    window = VideoLocalizerApp()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()