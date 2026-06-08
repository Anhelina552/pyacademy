from django.test import TestCase
# Імпортуємо тільки ваші моделі
# Замініть from .models на:
from courses.models import Course, Lesson, LessonBlock
from django.test import Client


class LessonModelTest(TestCase):
    def setUp(self):
        # Створюємо тестові дані
        self.course = Course.objects.create(title="Python для початківців")
        self.lesson = Lesson.objects.create(title="Hello World", course=self.course)

        # Використовуємо 'block_title' замість 'title'
        self.block = LessonBlock.objects.create(
            block_title="Вступ",
            block_text="Це приклад тексту для блоку.",
            lesson=self.lesson,
            order=1
        )

    def test_lesson_block_relationship(self):
        # Перевірка зв'язків
        self.assertEqual(self.block.lesson.title, "Hello World")
        self.assertEqual(self.block.lesson.course.title, "Python для початківців")
        # Перевірка вмісту блоку
        self.assertEqual(self.block.block_title, "Вступ")