from PySide6.QtCore import QThread, Signal
from src.core.video_processor import VideoProcessor


class VideoProcessorWorker(QThread):
    finished = Signal(str, str, str)  # original_subs, translated_subs, output_path
    error = Signal(str)
    progress = Signal(int)

    def __init__(self, video_path, output_dir, model_type, voice_name, hard_subtitles, only_subtitles):
        super().__init__()
        self.video_path = video_path
        self.output_dir = output_dir
        self.model_type = model_type
        self.voice_name = voice_name
        self.hard_subtitles = hard_subtitles
        self.only_subtitles = only_subtitles

    def run(self):
        try:
            processor = VideoProcessor()
            output_video, output_srt_ru, output_srt_original = processor.create_localized_video(
                self.video_path,
                model_type=self.model_type,
                speaker_voice=self.voice_name,
                hard_subtitles=self.hard_subtitles,
                only_subtitles=self.only_subtitles,
                output_video=self.output_dir
            )

            with open(output_srt_original, 'r', encoding='utf-8') as f:
                original_content = f.read()

            with open(output_srt_ru, 'r', encoding='utf-8') as f:
                translated_content = f.read()

            self.finished.emit(original_content, translated_content, output_video)
        except Exception as e:
            self.error.emit(str(e))
