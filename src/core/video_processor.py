import os
import warnings
import pysrt
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, TextClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip
from pydub import AudioSegment
from src.core.translator import Translator
from src.core.tts import VoiceGenerator
from src.core.speech_recognition import SpeechRecognizer

warnings.filterwarnings("ignore")
FFMPEG_PATH = r"config\ffmpeg.exe"
MODEL_PATH = r"D:\PythonProject\HuggingFaceModels"
AudioSegment.ffmpeg = FFMPEG_PATH
os.environ["PATH"] += os.pathsep + os.path.dirname(FFMPEG_PATH)


#from transformers import AutoProcessor, SeamlessM4Tv2Model

class VideoProcessor:
    def __init__(self):
        pass

    def create_hard_subtitles(self, subtitles, video):
        def subtitle_generator(txt):
            return TextClip(
                text=txt,
                font=r'..\..\config/fonts/arial.ttf',
                font_size=24,
                color="white",
                stroke_color="black",
                size=video.size,
                method="caption",
                text_align="center",
                vertical_align="bottom"
            )

        subs_ru = SubtitlesClip(subtitles, make_textclip=subtitle_generator, encoding='utf-8')
        return CompositeVideoClip([video, subs_ru])

    def extract_audio_from_video(self, video_path, audio_output=r"..\..\data\temp_audio.wav"):
        """Извлечение аудио из видео файла"""
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(audio_output)
        return audio_output

    def create_localized_video(self,
                               video_path,
                               speaker_voice,
                               hard_subtitles=False,
                               only_subtitles=False,
                               model_type="marianMT",
                               output_video=r"..\..\data\video\localized_video.mp4",
                               output_srt_ru=r"..\..\data\subtitles\localized_subs_ru.srt",
                               output_srt_en=r"..\..\data\subtitles\original_subs_en.srt"):
        audio_path = self.extract_audio_from_video(video_path)

        print("Транскрибируем аудио...")
        speech_recognizer = SpeechRecognizer()
        transcription = speech_recognizer.transcribe_audio(audio_path)

        subs_en = pysrt.SubRipFile()
        for i, segment in enumerate(transcription['segments'], 1):
            sub_en = pysrt.SubRipItem()
            sub_en.index = i
            sub_en.start.seconds = segment['start']
            sub_en.end.seconds = segment['end']
            sub_en.text = segment['text']
            subs_en.append(sub_en)

        subs_en.save(output_srt_en, encoding='utf-8')
        print(f"Английские субтитры сохранены в {output_srt_en}")

        translator = Translator(model_type=model_type)
        translator.translate_srt_file(output_srt_en, output_srt_ru)
        print(f"Русские субтитры сохранены в {output_srt_ru}")

        if only_subtitles:
            if hard_subtitles:
                video = VideoFileClip(video_path)
                video = self.create_hard_subtitles(output_srt_ru, video)
                video.write_videofile(
                    output_video,
                    codec='libx264',
                    audio_codec='aac',
                    threads=4
                )
            return output_video, output_srt_ru, output_srt_en

        ru_subs = pysrt.open(output_srt_ru, encoding='utf-8')
        full_translated_text = " ".join(sub.text for sub in ru_subs)

        print("Создаем русскую озвучку...")
        voice_generator = VoiceGenerator()
        voice_path = voice_generator.text_to_speech(full_translated_text, speaker_voice)

        video = VideoFileClip(video_path)
        original_audio = video.audio.with_volume_scaled(0.5)

        russian_audio = AudioFileClip(voice_path)
        final_audio = CompositeAudioClip([original_audio, russian_audio])

        if hard_subtitles:
            video = self.create_hard_subtitles(output_srt_ru, video)

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


if __name__ == "__main__":
    localizer = VideoProcessor()
    sub_translator = Translator()

    print("1. Создать локализованное видео с русской озвучкой и субтитрами")
    print("2. Перевести существующий файл субтитров")
    choice = input("Выберите действие (1/2): ")

    if choice == "1":
        video_path = input("Введите путь к видео файлу: ")
        output_name = input("Введите имя выходного файла (без расширения): ")
        localizer.create_localized_video(video_path)
    elif choice == "2":
        srt_path = input("Введите путь к файлу .srt: ")
        sub_translator.translate_srt_file(srt_path)
    else:
        print("Неверный выбор")
