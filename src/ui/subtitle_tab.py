import os
import re
import sys

import pysrt

import src.ui.styles as style
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFileDialog, QWidget, QTextEdit, QComboBox, QMessageBox, QTabWidget,
                               QGroupBox, QProgressBar)
from PySide6.QtCore import Qt, QTimer
from src.ui.workers.subtitle_worker import SubtitleTranslatorWorker
from src.core.translator import Translator


class SubtitleTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.subtitles = ""
        self.subtitles_path = ""
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса для режима субтитров"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # 1. Панель загрузки субтитров
        load_panel = QHBoxLayout()
        load_panel.setSpacing(10)

        self.btn_load_srt = QPushButton(self.tr("Загрузить субтитры (.srt)"))
        self.btn_load_srt.setFixedHeight(40)
        self.btn_load_srt.setStyleSheet("""
                    QPushButton {
                        font-size: 14px;
                        padding: 8px;
                        background: #FBBC05;
                        color: white;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background: #E9AB04;
                    }
                """)
        self.btn_load_srt.clicked.connect(self.load_srt_file)

        self.lbl_subtitles = QLabel(self.tr("Файл не выбран"))
        self.lbl_subtitles.setStyleSheet("font-size: 12px; color: #666;")
        self.lbl_subtitles.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        load_panel.addWidget(self.btn_load_srt)
        load_panel.addWidget(self.lbl_subtitles, stretch=1)

        # 2. Настройки перевода
        self.translate_settings = QGroupBox(self.tr("Настройки перевода"))
        self.translate_settings.setStyleSheet(style.GROUP_BOX_STYLE)
        translate_layout = QHBoxLayout()

        self.lang_combo = QComboBox()
        self.lang_combo.addItems([self.tr("Английский → Русский")])
        self.lang_combo.setCurrentIndex(0)
        self.lang_combo.setStyleSheet("""
                    QComboBox {
                        padding: 6px;
                        font-size: 14px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                    }
                """)
        self.model_label = QLabel(self.tr("Модель перевода:"))
        translate_layout.addWidget(QLabel(self.model_label))
        self.model_combo = QComboBox()
        self.model_combo.addItems([self.tr("MarianMT (быстрая)"), self.tr("NLLB (медленная) Требуется 6GB VRAM!")])
        self.model_combo.setStyleSheet("""
                    QComboBox {
                        padding: 6px;
                        font-size: 14px;
                        border: 1px solid #ddd;
                        border-radius: 4px;
                    }
                """)
        translate_layout.addWidget(self.model_combo)

        self.btn_translate_srt = QPushButton(self.tr("Перевести субтитры"))
        self.btn_translate_srt.setFixedHeight(40)
        self.btn_translate_srt.setEnabled(False)
        self.btn_translate_srt.setStyleSheet("""
                    QPushButton {
                        padding: 8px;
                        font-size: 14px;
                        background: #34A853;
                        color: white;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background: #2D9248;
                    }
                    QPushButton:disabled {
                        background: #CCCCCC;
                    }
                """)
        self.btn_translate_srt.clicked.connect(self.translate_subtitles)
        self.language_label = QLabel(self.tr("Язык перевода:"))
        translate_layout.addWidget(self.language_label)
        translate_layout.addWidget(self.lang_combo, stretch=1)
        translate_layout.addWidget(self.btn_translate_srt)
        self.translate_settings.setLayout(translate_layout)

        # 3. Панель субтитров
        self.subtitle_tabs = QTabWidget()
        self.subtitle_tabs.setStyleSheet(style.TAB_STYLE)

        self.original_subtitle_view = QTextEdit()
        self.original_subtitle_view.setReadOnly(False)
        self.original_subtitle_view.setPlaceholderText(self.tr("Оригинальные субтитры..."))
        self.original_subtitle_view.setStyleSheet("""
                    QTextEdit {
                        font-family: 'Consolas';
                        font-size: 12px;
                        padding: 10px;
                    }
                """)

        self.translated_subtitle_view = QTextEdit()
        self.translated_subtitle_view.setReadOnly(False)
        self.translated_subtitle_view.setPlaceholderText(self.tr("Переведённые субтитры..."))
        self.translated_subtitle_view.setStyleSheet("""
                    QTextEdit {
                        font-family: 'Consolas';
                        font-size: 12px;
                        padding: 10px;
                    }
                """)

        self.subtitle_tabs.addTab(self.original_subtitle_view, self.tr("Оригинал"))
        self.subtitle_tabs.addTab(self.translated_subtitle_view, self.tr("Перевод"))

        # 4. Кнопка экспорта
        self.btn_export = QPushButton(self.tr("Экспорт субтитров"))
        self.btn_export.setEnabled(False)
        self.btn_export.setFixedHeight(45)
        self.btn_export.setStyleSheet("""
                    QPushButton {
                        background: #EA4335;
                        color: white;
                        font-weight: bold;
                        font-size: 16px;
                        padding: 8px;
                        border-radius: 4px;
                    }
                    QPushButton:hover {
                        background: #D33426;
                    }
                    QPushButton:disabled {
                        background: #CCCCCC;
                    }
                """)
        self.btn_export.clicked.connect(self.export_subtitles)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet(style.PROGRESS_BAR)

        # Собираем все вместе
        layout.addLayout(load_panel)
        layout.addWidget(self.translate_settings)
        layout.addWidget(self.subtitle_tabs, stretch=1)
        layout.addWidget(self.btn_export)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def load_srt_file(self):
        """Загрузка файла субтитров"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл субтитров",
            "",
            "Subtitle Files (*.srt)"
        )

        if path:
            self.subtitles_path = path
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.subtitles = f.read()
                self.original_subtitle_view.setPlainText(self.subtitles)
                self.btn_translate_srt.setEnabled(True)
                self.lbl_subtitles.setText(path.split("/")[-1])
                self.parent.update_status_bar(self.tr(f"Загружены субтитры: {path.split('/')[-1]}"))
            except Exception as e:
                QMessageBox.warning(self, self.tr("Ошибка"), self.tr(f"Не удалось загрузить файл субтитров: {str(e)}"))

    def translate_subtitles(self):
        """Перевод загруженных субтитров"""
        if not self.subtitles:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Субтитры не загружены!"))
            return
        self.btn_load_srt.setEnabled(False)
        self.btn_translate_srt.setEnabled(False)
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.parent.update_status_bar(self.tr("Идет перевод субтитров..."))

        model_type = "marianMT" if self.model_combo.currentIndex() == 0 else "nllb"

        self.thread = SubtitleTranslatorWorker(self.subtitles_path, model_type)
        self.thread.finished.connect(self.on_translation_finished)
        self.thread.error.connect(self.on_translation_error)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.start()

    def on_translation_finished(self, translated_content):
        self.translated_subtitle_view.setPlainText(translated_content)
        self.parent.update_status_bar(self.tr("Перевод субтитров завершен!"))
        self.btn_load_srt.setEnabled(True)
        self.btn_translate_srt.setEnabled(True)
        self.btn_export.setEnabled(True)
        self.progress.setVisible(False)

    def on_translation_error(self, error_message):
        QMessageBox.warning(self, self.tr("Ошибка"), self.tr(f"Ошибка при переводе: {error_message}"))
        self.progress.setVisible(False)

    def export_subtitles(self):
        """Экспорт субтитров в выбранную папку"""
        original_content = self.original_subtitle_view.toPlainText()
        translated_content = self.translated_subtitle_view.toPlainText()
        if not translated_content:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Нет переведенных субтитров для экспорта!"))
            return

        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения субтитров",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if not output_dir:
            return

        try:
            original_path = f"{output_dir}/original_subtitles.srt"
            with open(original_path, 'w', encoding='utf-8') as f:
                f.write(original_content)

            translated_path = f"{output_dir}/translated_subtitles.srt"
            with open(translated_path, 'w', encoding='utf-8') as f:
                f.write(translated_content)

            self.parent.update_status_bar(self.tr(f"Субтитры сохранены в: {output_dir}"))
            QMessageBox.information(self, self.tr("Успех"), self.tr("Субтитры успешно экспортированы!"))
        except Exception as e:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr(f"Не удалось сохранить субтитры: {str(e)}"))

    def retranslate_ui(self):
        # Кнопки
        self.btn_load_srt.setText(self.tr("Загрузить субтитры (.srt)"))
        self.btn_translate_srt.setText(self.tr("Перевести субтитры"))
        self.btn_export.setText(self.tr("Экспорт субтитров"))

        # Метки
        self.lbl_subtitles.setText(self.tr("Файл не выбран"))

        # Группы настроек
        self.model_label.setText(self.tr("Модель перевода:"))
        self.language_label.setText(self.tr("Язык перевода:"))
        self.translate_settings.setTitle(self.tr("Настройки перевода"))
        self.lang_combo.setItemText(0, self.tr("Английский → Русский"))
        self.model_combo.setItemText(0, self.tr("MarianMT (быстрая)"))
        self.model_combo.setItemText(1, self.tr("NLLB (медленная) Требуется 6GB VRAM!"))

        # Субтитры
        self.subtitle_tabs.setTabText(0, self.tr("Оригинал"))
        self.subtitle_tabs.setTabText(1, self.tr("Перевод"))
        self.original_subtitle_view.setPlaceholderText(self.tr("Оригинальные субтитры..."))
        self.translated_subtitle_view.setPlaceholderText(self.tr("Переведённые субтитры..."))


