import gc
import os

import torch.cuda

os.environ["HF_HOME"] = r"D:\PythonProject\HuggingFaceModels"
import nltk
import pysrt
from transformers import MarianMTModel, MarianTokenizer
from src.core.config import DEVICE
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class Translator:
    def __init__(self, model_type="marianMT"):
        #MarianMT
        self.model_type = model_type
        if self.model_type == "marianMT":
            self.tokenizer = MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-ru")
            self.translation_model = MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-ru").to(DEVICE)
        #NLLB
        elif self.model_type == "nllb":
            self.translation_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/nllb-200-1.3B").to(DEVICE)
            self.tokenizer = AutoTokenizer.from_pretrained("facebook/nllb-200-1.3B")
        else:
            raise ValueError("Unsupported model type")

    def clean_memory(self):
        del self.translation_model
        gc.collect()
        torch.cuda.empty_cache()
        return None

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
                ).to(DEVICE)
                if self.model_type == "nllb":
                    outputs = self.translation_model.generate(**inputs, forced_bos_token_id=self.tokenizer.convert_tokens_to_ids("rus_Cyrl"))
                else:
                    outputs = self.translation_model.generate(**inputs)
                translated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                translated_sentences.append(translated)
            except Exception as e:
                print(f"Ошибка перевода предложения: '{sentence}'. Ошибка: {e}")
                translated_sentences.append(sentence)

        translated_text = " ".join(translated_sentences)
        return translated_text, remaining_context

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
            self.clean_memory()
            return "\n".join(translated_subs)

        except Exception as e:
            print(f"Ошибка обработки файла: {e}")
            return None
