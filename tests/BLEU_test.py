import random
from pathlib import Path
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from sacrebleu import corpus_bleu

# 1. Конфигурация
MODEL_NAME = "Helsinki-NLP/opus-mt-en-ru"  # Модель перевода
EN_FILE = r"D:\PythonProject\Diplom\tests\datasets\Translation\paracrawl-release1.en-ru.zipporah0-dedup-clean.en"  # Путь к файлу с английскими предложениями
RU_FILE = r"D:\PythonProject\Diplom\tests\datasets\Translation\paracrawl-release1.en-ru.zipporah0-dedup-clean.ru"  # Путь к файлу с русскими переводами
SAMPLE_SIZE = 500  # Количество примеров для оценки
SEED = 42  # Для воспроизводимости результатов
MAX_LENGTH = 512  # Максимальная длина предложения


# 2. Загрузка данных
def load_parallel_texts(en_path, ru_path, sample_size=None, seed=None):
    """Загружает параллельные тексты из файлов"""
    if seed:
        random.seed(seed)

    with open(en_path, 'r', encoding='utf-8') as f_en, \
            open(ru_path, 'r', encoding='utf-8') as f_ru:
        en_lines = [line.strip() for line in f_en if line.strip()]
        ru_lines = [line.strip() for line in f_ru if line.strip()]

    # Проверка согласованности данных
    if len(en_lines) != len(ru_lines):
        print(f"Предупреждение: разное количество строк ({len(en_lines)} en vs {len(ru_lines)} ru)")
        min_lines = min(len(en_lines), len(ru_lines))
        en_lines = en_lines[:min_lines]
        ru_lines = ru_lines[:min_lines]

    # Создаем пары предложений
    pairs = list(zip(en_lines, ru_lines))

    # Выборка (если нужно)
    if sample_size and sample_size < len(pairs):
        pairs = random.sample(pairs, sample_size)

    return pairs


# 3. Загрузка модели
def load_model(model_name):
    """Загружает модель и токенизатор"""
    print(f"Загрузка модели {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    return tokenizer, model


# 4. Функция перевода
def translate(text, tokenizer, model, max_length=512):
    """Переводит текст с помощью модели"""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=max_length)
    outputs = model.generate(**inputs)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


# 5. Оценка качества
def evaluate_bleu(test_data, tokenizer, model, num_examples=5):
    """Вычисляет BLEU score и выводит примеры"""
    print("\nНачало оценки перевода...")

    # Перевод и подготовка данных для BLEU
    references = [[ru] for en, ru in test_data]
    hypotheses = [translate(en, tokenizer, model) for en, _ in test_data]

    # Расчет BLEU
    bleu_score = corpus_bleu(hypotheses, references)
    print(f"\nBLEU score: {bleu_score.score:.2f}")
    print(f"Детализация: {bleu_score}")

    # Вывод примеров
    print("\nПримеры переводов:")
    for i in range(min(num_examples, len(test_data))):
        print(f"\nПример {i + 1}:")
        print(f"EN: {test_data[i][0]}")
        print(f"RU эталон: {test_data[i][1]}")
        print(f"RU модель: {hypotheses[i]}")

    return bleu_score.score


# Основная функция
def main():
    try:
        # Проверка файлов
        if not Path(EN_FILE).exists() or not Path(RU_FILE).exists():
            raise FileNotFoundError("Файлы с данными не найдены")

        # Загрузка данных
        print("Загрузка данных...")
        test_data = load_parallel_texts(EN_FILE, RU_FILE, sample_size=SAMPLE_SIZE, seed=SEED)
        print(f"Загружено {len(test_data)} пар предложений")

        # Загрузка модели
        tokenizer, model = load_model(MODEL_NAME)

        # Оценка качества
        evaluate_bleu(test_data, tokenizer, model)

    except Exception as e:
        print(f"\nОшибка: {e}")
        print("Проверьте:")
        print("- Пути к файлам EN и RU")
        print("- Формат файлов (одно предложение на строку)")
        print("- Кодировку файлов (должна быть UTF-8)")


if __name__ == "__main__":
    main()