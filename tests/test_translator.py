import unittest
from src.core.translator import Translator


class TestTranslateWithContext(unittest.TestCase):
    def setUp(self):
        self.marian_translator = Translator(model_type="marianMT")

    def test_translate_simple_sentence(self):
        """T1: Перевод простого предложения"""
        text = "Hello world."
        previous_context = ""
        translated, remaining_context = self.marian_translator.translate_text_with_context(text, previous_context)
        self.assertIn("привет", translated.lower())
        self.assertIn("мир", translated.lower())
        self.assertEqual(remaining_context, "")

    def test_translate_incomplete_sentence(self):
        """T2: Перевод незавершённого предложения"""
        text = "This is an example of a sentence that"  # Нет точки — предложение не завершено
        previous_context = ""
        translated, remaining_context = self.marian_translator.translate_text_with_context(text, previous_context)
        self.assertEqual(translated, "")
        self.assertEqual(remaining_context, text)

    def test_translate_with_context(self):
        """Тест перевода с учетом контекста"""
        context = "The weather is nice"
        text = "Today is sunny"

        # Переводим сначала контекст
        translated_context, _ = self.marian_translator.translate_text_with_context(context)

        # Переводим основной текст с контекстом
        result, remaining_context = self.marian_translator.translate_text_with_context(text, translated_context)

        self.assertNotEqual(result, text)
        self.assertEqual(remaining_context, "")


if __name__ == '__main__':
    unittest.main()
