import os
import src.ui.styles as style
from PySide6.QtWidgets import (QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QFileDialog, QWidget,
                               QProgressBar, QTextEdit, QComboBox, QMessageBox, QTabWidget, QGroupBox, QRadioButton,
                               QCheckBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import (QPixmap, QPainter, QFont)
from src.ui.workers.video_worker import VideoProcessorWorker


class VideoTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.video_path = ""
        self.output_dir = ""
        self.init_ui()

    def init_ui(self):
        """Инициализация интерфейса для режима видео"""
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # 1. Панель загрузки видео
        load_panel = QHBoxLayout()
        load_panel.setSpacing(10)

        self.btn_load = QPushButton(self.tr("Загрузить видео"))
        self.btn_load.setFixedHeight(40)
        self.btn_load.setStyleSheet(style.PRIMARY_BUTTON)
        self.btn_load.clicked.connect(self.load_video)

        self.lbl_video = QLabel(self.tr("Файл не выбран"))
        self.lbl_video.setStyleSheet("font-size: 12px; color: #666;")
        self.lbl_video.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        load_panel.addWidget(self.btn_load)
        load_panel.addWidget(self.lbl_video, stretch=1)

        # 2. Панель предпросмотра
        self.lbl_preview = QLabel()
        self.lbl_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_preview.setStyleSheet(style.PREVIEW_LABEL)
        self.lbl_preview.setText(self.tr("Предпросмотр видео появится здесь"))
        self.lbl_preview.setMinimumHeight(200)

        # 3. Панель настроек видео
        settings_layout = QHBoxLayout()
        settings_layout.setSpacing(15)

        # Настройки голоса и перевода
        left_settings = QVBoxLayout()
        left_settings.setSpacing(10)

        # Группа настроек голоса
        self.voice_group = QGroupBox(self.tr("Настройки озвучки"))
        self.voice_group.setStyleSheet(style.GROUP_BOX_STYLE)
        voice_layout = QVBoxLayout()
        voice_type_group = QHBoxLayout()
        self.male_voice = QRadioButton(self.tr("Мужской"))
        self.male_voice.setChecked(True)
        self.female_voice = QRadioButton(self.tr("Женский"))
        voice_type_group.addWidget(self.male_voice)
        voice_type_group.addWidget(self.female_voice)

        self.subtitles_only = QCheckBox(self.tr("Только субтитры (без озвучки)"))
        self.subtitles_only.setStyleSheet("font-size: 14px; spacing: 5px;")

        self.hard_subtitles = QCheckBox(self.tr("Вшить субтитры в видео (жесткие субтитры)"))
        self.hard_subtitles.setStyleSheet("font-size: 14px; spacing: 5px;")

        voice_layout.addLayout(voice_type_group)
        voice_layout.addWidget(self.subtitles_only)
        voice_layout.addWidget(self.hard_subtitles)
        self.voice_group.setLayout(voice_layout)

        # Группа настроек перевода
        self.translate_group = QGroupBox(self.tr("Настройки перевода"))
        self.translate_group.setStyleSheet(style.GROUP_BOX_STYLE)
        translate_layout = QVBoxLayout()

        model_layout = QHBoxLayout()
        self.model_label = QLabel(self.tr("Модель перевода:"))
        model_layout.addWidget(self.model_label)
        self.model_combo_video = QComboBox()
        self.model_combo_video.addItems([self.tr("MarianMT (быстрая)"), self.tr("NLLB (медленная) Требуется 6GB VRAM!")])
        self.model_combo_video.setStyleSheet("""
                   QComboBox {
                       padding: 6px;
                       font-size: 14px;
                       border: 1px solid #ddd;
                       border-radius: 4px;
                   }
               """)
        model_layout.addWidget(self.model_combo_video, stretch=1)
        translate_layout.addLayout(model_layout)

        lang_layout = QHBoxLayout()
        self.lang_label = QLabel(self.tr("Язык перевода:"))
        lang_layout.addWidget(self.lang_label)
        self.lang_combo_video = QComboBox()
        self.lang_combo_video.addItems([self.tr("Английский → Русский")])
        self.lang_combo_video.setStyleSheet("""
                   QComboBox {
                       padding: 6px;
                       font-size: 14px;
                       border: 1px solid #ddd;
                       border-radius: 4px;
                   }
               """)

        lang_layout.addWidget(self.lang_combo_video, stretch=1)

        translate_layout.addLayout(lang_layout)
        self.translate_group.setLayout(translate_layout)

        left_settings.addWidget(self.voice_group)
        left_settings.addWidget(self.translate_group)
        left_settings.addStretch()

        # Панель субтитров
        right_settings = QVBoxLayout()
        right_settings.setSpacing(10)

        subtitle_group = QGroupBox(self.tr("Субтитры"))
        subtitle_group.setStyleSheet(style.GROUP_BOX_STYLE)
        subtitle_layout = QVBoxLayout()

        self.subtitle_tabs_video = QTabWidget()
        self.subtitle_tabs_video.setStyleSheet(style.TAB_STYLE)

        self.original_subtitle_view_video = QTextEdit()
        self.original_subtitle_view_video.setReadOnly(False)
        self.original_subtitle_view_video.setPlaceholderText(self.tr("Оригинальные субтитры..."))
        self.original_subtitle_view_video.setStyleSheet("""
                   QTextEdit {
                       font-family: 'Consolas';
                       font-size: 12px;
                       padding: 10px;
                   }
               """)

        self.translated_subtitle_view_video = QTextEdit()
        self.translated_subtitle_view_video.setReadOnly(False)
        self.translated_subtitle_view_video.setPlaceholderText(self.tr("Переведённые субтитры..."))
        self.translated_subtitle_view_video.setStyleSheet("""
                   QTextEdit {
                       font-family: 'Consolas';
                       font-size: 12px;
                       padding: 10px;
                   }
               """)

        self.subtitle_tabs_video.addTab(self.original_subtitle_view_video, self.tr("Оригинал"))
        self.subtitle_tabs_video.addTab(self.translated_subtitle_view_video, self.tr("Перевод"))

        subtitle_layout.addWidget(self.subtitle_tabs_video)
        subtitle_group.setLayout(subtitle_layout)

        right_settings.addWidget(subtitle_group)

        settings_layout.addLayout(left_settings)
        settings_layout.addLayout(right_settings)

        # 4. Панель кнопок
        button_panel = QHBoxLayout()
        button_panel.setSpacing(10)

        self.btn_process = QPushButton(self.tr("Обработать видео"))
        self.btn_process.setEnabled(False)
        self.btn_process.setFixedHeight(45)
        self.btn_process.setStyleSheet(style.PRIMARY_BUTTON)
        self.btn_process.clicked.connect(self.process_video)

        self.btn_export_video = QPushButton(self.tr("Экспорт субтитров"))
        self.btn_export_video.setEnabled(False)
        self.btn_export_video.setFixedHeight(45)
        self.btn_export_video.setStyleSheet(style.ACCENT_BUTTON)
        # self.btn_export_video.clicked.connect(lambda: self.export_subtitles(video_mode=True))

        button_panel.addWidget(self.btn_process)
        button_panel.addWidget(self.btn_export_video)

        # 5. Прогресс-бар
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setStyleSheet(style.PROGRESS_BAR)

        layout.addLayout(load_panel)
        layout.addWidget(self.lbl_preview)
        layout.addLayout(settings_layout)
        layout.addLayout(button_panel)
        layout.addWidget(self.progress)

        self.setLayout(layout)

    def load_video(self):
        """Загрузка видеофайла"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите видеофайл",
            "",
            "Video Files (*.mp4 *.avi *.mov)"
        )

        if path:
            self.video_path = path
            self.lbl_video.setText(path.split("/")[-1])
            self.btn_process.setEnabled(True)
            self.parent.update_status_bar(self.tr(f"Загружено видео: {path}"))
            self.show_video_thumbnail(path)

    def process_video(self):
        if not self.video_path:
            QMessageBox.warning(self, self.tr("Ошибка"), self.tr("Видеофайл не выбран!"))
            return

        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения результатов",
            "",
            QFileDialog.Option.ShowDirsOnly
        )

        if not output_dir:
            return

        if output_dir:
            file_name = "localized_video.mp4"
            output_dir = os.path.join(output_dir, file_name)

        self.output_dir = output_dir
        self.progress.setVisible(True)
        self.btn_process.setEnabled(False)
        self.btn_load.setEnabled(False)
        self.parent.update_status_bar(self.tr("Идет обработка видео..."))

        voice_name = 'Ferran Simen' if self.male_voice.isChecked() else 'Claribel Dervla'
        only_sub_parameter = True if self.subtitles_only.isChecked() else False
        hard_subtitles_parameter = True if self.hard_subtitles.isChecked() else False
        model_type = "marianMT" if self.model_combo_video.currentIndex() == 0 else "nllb"
        self.thread = VideoProcessorWorker(self.video_path, self.output_dir, model_type, voice_name,
                                           hard_subtitles_parameter, only_sub_parameter)
        self.thread.finished.connect(self.on_video_processing_finish)
        self.thread.error.connect(self.on_video_processing_error)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.start()
        self.progress_value = 0
        self.progress.setValue(0)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(10)

    def on_video_processing_error(self, error_message):
        QMessageBox.warning(self, self.tr("Ошибка"), self.tr(f"Ошибка при обработке: {error_message}"))
        self.progress.setVisible(False)
        self.btn_process.setEnabled(True)

    def on_video_processing_finish(self, original_content, translated_content, output_path):
        """Завершение обработки"""
        self.original_subtitle_view_video.setPlainText(original_content)
        self.translated_subtitle_view_video.setPlainText(translated_content)
        self.parent.update_status_bar(self.tr(f"Обработка завершена! Результаты сохранены в: {self.output_dir}"))
        self.btn_export_video.setEnabled(True)
        self.btn_process.setEnabled(True)
        self.btn_load.setEnabled(True)
    def show_video_thumbnail(self, path):
        """Показывает первый кадр видео (заглушка)"""
        pixmap = QPixmap(800, 300)
        pixmap.fill(Qt.darkGray)

        painter = QPainter(pixmap)
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 16))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, self.tr("Превью видео: ") + path.split("/")[-1])
        painter.end()

        self.lbl_preview.setPixmap(pixmap)

    def update_progress(self):
        """Обновление прогресс-бара"""
        self.progress_value += 1
        self.progress.setValue(self.progress_value)

        if self.progress_value >= 100:
            self.timer.stop()

    def export_subtitles(self):
        """Экспорт субтитров в выбранную папку"""
        original_content = self.original_subtitle_view_video.toPlainText()
        translated_content = self.translated_subtitle_view_video.toPlainText()
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
        """Обновление текстов в режиме видео"""
        self.btn_load.setText(self.tr("Загрузить видео"))
        self.lbl_video.setText(self.tr("Файл не выбран"))
        self.lbl_preview.setText(self.tr("Предпросмотр видео появится здесь"))
        self.btn_process.setText(self.tr("Обработать видео"))
        self.btn_export_video.setText(self.tr("Экспорт субтитров"))

        # Группы настроек
        self.lang_label.setText(self.tr("Язык перевода:"))
        self.model_label.setText(self.tr("Модель перевода:"))
        self.voice_group.setTitle(self.tr("Настройки озвучки"))
        self.male_voice.setText(self.tr("Мужской"))
        self.female_voice.setText(self.tr("Женский"))
        self.subtitles_only.setText(self.tr("Только субтитры (без озвучки)"))
        self.hard_subtitles.setText(self.tr("Вшить субтитры в видео (жесткие субтитры)"))

        self.translate_group.setTitle(self.tr("Настройки перевода"))
        self.lang_combo_video.setItemText(0, self.tr("Английский → Русский"))
        self.model_combo_video.setItemText(0, self.tr("MarianMT (быстрая)"))
        self.model_combo_video.setItemText(1, self.tr("NLLB (медленная) Требуется 6GB VRAM!"))

        # Субтитры
        self.subtitle_tabs_video.setTabText(0, self.tr("Оригинал"))
        self.subtitle_tabs_video.setTabText(1, self.tr("Перевод"))
        self.original_subtitle_view_video.setPlaceholderText(self.tr("Оригинальные субтитры..."))
        self.translated_subtitle_view_video.setPlaceholderText(self.tr("Переведённые субтитры..."))

