import gc

import torch
import whisper
from src.core.config import DEVICE


class SpeechRecognizer:
    def __init__(self):
        self.model = whisper.load_model("base").to(DEVICE)

    def clean_memory(self):
        del self.model
        gc.collect()
        torch.cuda.empty_cache()
        return None

    def transcribe_audio(self, audio_path):
        """Транскрибация аудио в текст"""
        result = self.model.transcribe(audio_path)
        self.clean_memory()
        print(result)
        return result
