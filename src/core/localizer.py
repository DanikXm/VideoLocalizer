import os

import nltk
import torch
import whisper
import pysrt
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip
import warnings
from transformers import MarianMTModel, MarianTokenizer
from pydub import AudioSegment
from TTS.api import TTS

warnings.filterwarnings("ignore")
FFMPEG_PATH = r"config\ffmpeg.exe"
AudioSegment.ffmpeg = FFMPEG_PATH
os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_PATH)

device = "cuda" if torch.cuda.is_available() else "cpu"


class VideoLocalizer:
    def __init__(self):
        self.speech_model = whisper.load_model("base").to(device)
        self.translation_model_name = "Helsinki-NLP/opus-mt-en-ru"
        self.tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=False).to(device)
        self.tokenizer = MarianTokenizer.from_pretrained(self.translation_model_name)
        self.translation_model = MarianMTModel.from_pretrained(self.translation_model_name).to(device)
        self.context_cache = {}

    def transcribe_audio(self, audio_path):
        """Транскрибация аудио в текст"""
        result = self.speech_model.transcribe(audio_path)
        return result["text"]

    def translate_text_with_context(self, text, previous_context=""):
        """Перевод текста с учетом контекста из предыдущих субтитров."""
        if not text.strip():
            return text, ""

        # Объединяем предыдущий контекст с текущим текстом
        combined_text = previous_context + " " + text if previous_context else text
        sentences = nltk.sent_tokenize(combined_text, language='english')

        # Если предложение не завершено (нет точки в конце), сохраняем его как контекст
        translated_sentences = []
        remaining_context = ""

        for sentence in sentences:
            if not sentence.endswith(('.', '!', '?')):
                remaining_context = sentence
                continue

            try:
                inputs = self.tokenizer(
                    sentence,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512
                ).to(device)
                outputs = self.translation_model.generate(**inputs)
                translated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                translated_sentences.append(translated)
            except Exception as e:
                print(f"Ошибка перевода предложения: '{sentence}'. Ошибка: {e}")
                translated_sentences.append(sentence)

        translated_text = " ".join(translated_sentences)
        return translated_text, remaining_context

    def text_to_speech(self, text, speaker_voice, output_path=r"..\..\data\temp_voice.mp3"):
        """Синтез русской речи из текста"""
        self.tts.tts_to_file(text=text,
                                 speaker="Ferran Simen",  # Референсный голос
                                 language="ru",
                                 file_path=output_path)
        audio = AudioSegment.from_file(output_path)
        audio.export(output_path, format="mp3")
        return output_path

    def extract_audio_from_video(self, video_path, audio_output=r"..\..\data\temp_audio.wav"):
        """Извлечение аудио из видео файла"""
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_output)
        return audio_output

    def create_localized_video(self,
                               video_path,
                               speaker_voice,
                               only_subtitles=False,
                               output_video=r"..\..\data\video\localized_video.mp4",
                               output_srt_ru=r"..\..\data\subtitles\localized_subs_ru.srt",
                               output_srt_en=r"..\..\data\subtitles\original_subs_en.srt"):
        """Создание локализованного видео с сохранением субтитров на двух языках"""
        audio_path = self.extract_audio_from_video(video_path)

        print("Транскрибируем аудио...")
        transcription = self.speech_model.transcribe(audio_path)

        # Создаем английские субтитры
        subs_en = pysrt.SubRipFile()
        for i, segment in enumerate(transcription['segments'], 1):
            sub_en = pysrt.SubRipItem()
            sub_en.index = i
            sub_en.start.seconds = segment['start']
            sub_en.end.seconds = segment['end']
            sub_en.text = segment['text']
            subs_en.append(sub_en)

        # Сохраняем английские субтитры
        subs_en.save(output_srt_en, encoding='utf-8')
        print(f"Английские субтитры сохранены в {output_srt_en}")

        # Создаем русские субтитры
        self.translate_srt_file(output_srt_en, output_srt_ru)
        print(f"Русские субтитры сохранены в {output_srt_ru}")

        if only_subtitles:
            return output_video, output_srt_ru, output_srt_en

        # Получаем текст для озвучки из русских субтитров
        ru_subs = pysrt.open(output_srt_ru)
        full_translated_text = " ".join(sub.text for sub in ru_subs)

        # Создаем русскую озвучку
        print("Создаем русскую озвучку...")
        voice_path = self.text_to_speech(full_translated_text, speaker_voice)

        # Загружаем оригинальное видео и аудио
        video = VideoFileClip(video_path)
        original_audio = video.audio.with_volume_scaled(0.5)

        # Создаем композицию аудио
        russian_audio = AudioFileClip(voice_path)
        final_audio = CompositeAudioClip([original_audio, russian_audio])

        # Создаем финальное видео
        print("Создаем финальное видео...")
        final_video = video.with_audio(final_audio)
        final_video.write_videofile(
            output_video,
            codec='libx264',
            audio_codec='aac',
            threads=4
        )
        os.remove(audio_path)
        os.remove(voice_path)

        print(f"Локализованное видео сохранено в {output_video}")
        return output_video, output_srt_ru, output_srt_en

    def translate_srt_file(self, srt_path, output_srt=r"..\..\data\subtitles\translated.srt"):
        """Перевод файла субтитров с учетом контекста."""
        try:
            subs = pysrt.open(srt_path)
            translated_subs = []
            previous_context = ""

            for sub in subs:
                try:
                    sentences = sub.text.split('\n')
                    translated_lines = []
                    current_context = previous_context

                    for line in sentences:
                        if line.strip():
                            translated_line, current_context = self.translate_text_with_context(line, current_context)
                            translated_lines.append(translated_line)

                    sub.text = '\n'.join(translated_lines)
                    previous_context = current_context

                    translated_sub = f"{sub.index}\n{sub.start} --> {sub.end}\n{sub.text}\n"
                    translated_subs.append(translated_sub)

                except Exception as e:
                    print(f"Ошибка перевода строки {sub.index}: {e}")
                    sub.text = f"[ОШИБКА ПЕРЕВОДА] {sub.text}"
                    translated_sub = f"{sub.index}\n{sub.start} --> {sub.end}\n{sub.text}\n"
                    translated_subs.append(translated_sub)

            subs.save(output_srt, encoding='utf-8')
            print(f"Переведенные субтитры сохранены в {output_srt}")
            return "\n".join(translated_subs)

        except Exception as e:
            print(f"Ошибка обработки файла: {e}")
            return None