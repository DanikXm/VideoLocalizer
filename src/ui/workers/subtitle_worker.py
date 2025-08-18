from PySide6.QtCore import QThread, Signal
from src.core.translator import Translator


class SubtitleTranslatorWorker(QThread):
    finished = Signal(str)
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, subtitles_path, model_type):
        super().__init__()
        self.subtitles_path = subtitles_path
        self.model_type = model_type

    def run(self):
        try:
            translator = Translator(model_type=self.model_type)
            translated_content = translator.translate_srt_file(self.subtitles_path)
            self.finished.emit(translated_content)
        except Exception as e:
            self.error.emit(str(e))
