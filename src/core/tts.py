import gc
import torch
from TTS.api import TTS
from pydub import AudioSegment

from src.core.config import DEVICE


class VoiceGenerator:

    def __init__(self):
        self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2").to(DEVICE)

    def clean_memory(self):
        del self.tts
        gc.collect()
        torch.cuda.empty_cache()
        return None

    def text_to_speech(self, text, speaker_voice, output_path=r"..\..\data\temp_voice.mp3"):
        """Синтез русской речи из текста"""
        self.tts.tts_to_file(text=text,
                                 speaker=speaker_voice,
                                 language="ru",
                                 file_path=output_path)
        # Конвертируем в нужный формат
        audio = AudioSegment.from_file(output_path)
        audio.export(output_path, format="mp3")
        self.clean_memory()
        return output_path