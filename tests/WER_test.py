import os
import string

import jiwer
import whisper
from jiwer import wer, process_words

# --- 1. Настройки ---
model_name = "base"  # "tiny", "base", "small", "medium", "large"
audio_dir = r"D:\PythonProject\Diplom\tests\datasets\ASR\70968"  # Папка с аудиофайлами .flac
transcription_file = r"D:\PythonProject\Diplom\tests\datasets\ASR\70968\61-70968.trans.txt"  # Файл с транскрипциями


# --- 2. Загрузка транскрипций ---
def load_transcriptions(transcription_file):
    transcriptions = {}
    with open(transcription_file, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split(" ", 1)
            audio_id = parts[0]  # Например, "61-70968-0000"
            text = parts[1]  # Транскрипция
            transcriptions[audio_id] = text.lower()
    return transcriptions


transcriptions = load_transcriptions(transcription_file)

# --- 3. Подготовка аудиофайлов ---
audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith(".flac")])
references = []
audio_paths = []

for audio_file in audio_files:
    audio_id = os.path.splitext(audio_file)[0]  # Убираем .flac
    if audio_id in transcriptions:
        references.append(transcriptions[audio_id])
        audio_paths.append(os.path.join(audio_dir, audio_file))
    else:
        print(f"⚠ Транскрипция для {audio_file} не найдена!")

# --- 4. Загрузка модели Whisper ---
model = whisper.load_model(model_name)

# --- 5. Транскрибация аудио и сбор предсказаний ---
hypotheses = []
for audio_path in audio_paths:
    result = model.transcribe(audio_path)
    translator = str.maketrans('', '', string.punctuation)
    hypotheses.append(result["text"].translate(translator).lower())
    print(f"✅ Обработано: {os.path.basename(audio_path)}")


# --- 6. Расчет WER ---
error_rate = wer(
    references,
    hypotheses,
)

# --- 7. Вывод результатов ---
print("\n--- Результаты ---")
print(f"Обработано аудиофайлов: {len(audio_paths)}/{len(audio_files)}")
print(f"WER: {error_rate * 100:.2f}%")

# Примеры сравнения
print("\nПримеры:")
for i in range(min(3, len(audio_paths))):
    print(f"\nАудио: {os.path.basename(audio_paths[i])}")
    print(f"Эталон: {references[i]}")
    print(f"Whisper: {hypotheses[i]}")
