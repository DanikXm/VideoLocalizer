import os
import sys

from PySide6.QtCore import QTranslator

import src.ui.styles as style
from src.ui.video_tab import VideoTab
from src.ui.subtitle_tab import SubtitleTab
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                               QPushButton, QWidget, QStackedWidget, QMenuBar, QMenu)
from PySide6.QtGui import (QIcon, QColor, QAction, QActionGroup)


class VideoLocalizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoTranslator")
        self.setWindowIcon(QIcon("icon.png"))
        self.setMinimumSize(1200, 1000)
        self.setStyleSheet(style.MAIN_WINDOW_STYLE)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.translator = QTranslator()
        self.current_language = "ru"

        self.init_ui()
        self.change_language(self.current_language)

    def init_ui(self):
        #Меню бар
        menu_bar = self.menuBar()
        lang_menu = menu_bar.addMenu("Язык")

        self.lang_group = QActionGroup(self)
        self.lang_group.setExclusive(True)

        action_ru = QAction("Русский", self)
        action_en = QAction("English", self)
        action_ru.setCheckable(True)
        action_en.setCheckable(True)
        action_ru.setChecked(True)

        self.lang_group.addAction(action_ru)
        self.lang_group.addAction(action_en)

        lang_menu.addAction(action_ru)
        lang_menu.addAction(action_en)

        action_ru.triggered.connect(lambda: self.change_language("ru"))
        action_en.triggered.connect(lambda: self.change_language("en"))

        # Главный layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Переключатель режимов
        mode_selector = QHBoxLayout()
        mode_selector.setSpacing(0)

        self.btn_video_mode = QPushButton(self.tr("Режим видео"))
        self.btn_video_mode.setCheckable(True)
        self.btn_video_mode.setChecked(True)
        self.btn_video_mode.setStyleSheet(style.VIDEO_MODE_BUTTON)

        self.btn_subtitle_mode = QPushButton(self.tr("Режим субтитров"))
        self.btn_subtitle_mode.setCheckable(True)
        self.btn_subtitle_mode.setStyleSheet(style.SUBTITLE_MODE_BUTTON)

        mode_selector.addWidget(self.btn_video_mode)
        mode_selector.addWidget(self.btn_subtitle_mode)

        # Стек виджетов для разных режимов
        self.stacked_widget = QStackedWidget()

        # 1. Виджет для режима видео
        self.video_widget = VideoTab(parent=self)
        self.stacked_widget.addWidget(self.video_widget)

        # 2. Виджет для режима субтитров
        self.subtitle_widget = SubtitleTab(parent=self)
        self.stacked_widget.addWidget(self.subtitle_widget)

        self.btn_video_mode.clicked.connect(self.switch_to_video_mode)
        self.btn_subtitle_mode.clicked.connect(self.switch_to_subtitle_mode)

        main_layout.addLayout(mode_selector)
        main_layout.addWidget(self.stacked_widget)
        self.main_widget.setLayout(main_layout)

        self.status_bar = self.statusBar()
        self.update_status_bar(self.tr("Готов к работе"))

    def switch_to_video_mode(self):
        """Переключение в режим видео"""
        self.btn_video_mode.setChecked(True)
        self.btn_subtitle_mode.setChecked(False)
        self.stacked_widget.setCurrentIndex(0)
        self.update_status_bar(self.tr("Режим обработки видео"))

    def switch_to_subtitle_mode(self):
        """Переключение в режим субтитров"""
        self.btn_subtitle_mode.setChecked(True)
        self.btn_video_mode.setChecked(False)
        self.stacked_widget.setCurrentIndex(1)
        self.update_status_bar(self.tr("Режим обработки субтитров"))

    def change_language(self, lang_code):
        qm_file = f"../../config/ui_languages/{lang_code}.qm"
        if os.path.exists(qm_file):
            self.translator.load(qm_file)
            QApplication.instance().installTranslator(self.translator)
            self.update_ui_translations()
            self.current_lang = lang_code
        else:
            print(f"Перевод {lang_code} не найден!")

    def update_ui_translations(self):
        """Обновление текста всех элементов интерфейса"""
        self.btn_subtitle_mode.setText(self.tr("Режим субтитров"))
        self.btn_video_mode.setText(self.tr("Режим видео"))
        self.subtitle_widget.retranslate_ui()
        self.video_widget.retranslate_ui()
        self.centralWidget().update()

    def update_status_bar(self, message):
        self.status_bar.showMessage(message)

    def closeEvent(self, event):
        """Очистка при закрытии"""
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = app.palette()
    palette.setColor(palette.ColorRole.Window, QColor(240, 240, 240))
    app.setPalette(palette)

    window = VideoLocalizerApp()
    window.show()
    sys.exit(app.exec())
