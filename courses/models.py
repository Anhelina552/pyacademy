
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Course(models.Model):
    title = models.CharField(max_length=200, verbose_name="Назва курсу")
    description = models.TextField(verbose_name="Короткий опис для лендингу")

    def __str__(self):
        return self.title


class Lesson(models.Model):
    # Твої існуючі поля...
    course = models.ForeignKey('Course', on_delete=models.CASCADE, related_name='lessons', null=True, blank=True)
    number = models.PositiveIntegerField(verbose_name="Номер уроку", default=1)
    title = models.CharField(max_length=250, verbose_name="Заголовок сторінки")



    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ['number']

    def __str__(self):
        return f"Урок {self.number}: {self.title}"


class LessonBlock(models.Model):
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='blocks', verbose_name="Урок")
    block_title = models.CharField(max_length=250, verbose_name="Заголовок секції")
    block_text = models.TextField(verbose_name="Основний текст секції")
    block_image = models.ImageField(upload_to='lesson_blocks/', verbose_name="Додати зображення (якщо потрібно)",
                                    null=True, blank=True)
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок відображення (0, 1, 2...)")

    LAYOUT_CHOICES = [
        ('layout-standard', 'Стандартний (Текст на всю ширину)'),
        ('layout-author', 'Картка автора (Фото ЛІВОРУЧ, текст праворуч)'),
        ('layout-history', 'Історичний блок (Текст ліворуч, фото праворуч)'),
        ('layout-full-image', 'Велике фото (Фото на всю ширину, текст знизу)'),  # НАШ НОВИЙ МАКЕТ
    ]

    block_layout = models.CharField(
        max_length=50,
        choices=LAYOUT_CHOICES,
        default='layout-standard',
        verbose_name="Оберіть розташування елементів (Дизайн)"
    )

    class Meta:
        verbose_name = "Блок контенту уроку"
        verbose_name_plural = "Конструктор сторінки (Додати блоки тексту/картинок)"
        ordering = ['order']

    def __str__(self):
        return f"Секція: {self.block_title}"


class Term(models.Model):
    word = models.CharField(max_length=100, verbose_name="Термін")
    definition = models.TextField(verbose_name="Визначення")

    class Meta:
        verbose_name_plural = "Словник"
        ordering = ['word']

    def __str__(self):
        return self.word


class Quiz(models.Model):
    lesson = models.ForeignKey('Lesson', on_delete=models.CASCADE, related_name='quizzes')
    question = models.CharField(max_length=255, verbose_name="Запитання")
    option_a = models.CharField(max_length=100, verbose_name="Варіант А")
    option_b = models.CharField(max_length=100, verbose_name="Варіант Б")
    option_v = models.CharField(max_length=100, verbose_name="Варіант В (необов'язково)", blank=True, null=True)
    option_g = models.CharField(max_length=100, verbose_name="Варіант Г (необов'язково)", blank=True, null=True)
    correct_option = models.CharField(
        max_length=1,
        choices=[('a', 'А'), ('b', 'Б'), ('v', 'В'), ('g', 'Г')],
        verbose_name="Правильна відповідь"
    )

    def __str__(self):
        return f"Тест до уроку {self.lesson.number}: {self.question[:30]}..."
class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Користувач")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, verbose_name="Пройдений урок")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата проходження")

    class Meta:
        unique_together = ('user', 'lesson') # Захист, щоб один урок не зараховувався двічі одному й тому ж юзеру
        verbose_name = "Прогрес користувача"
        verbose_name_plural = "Прогрес користувачів"

    def __str__(self):
        return f"{self.user.username} -> Урок {self.lesson.number}"
class DictionaryTerm(models.Model):
    # Замінюємо max_width=100 на max_length=100
    word = models.CharField(max_length=100, unique=True, verbose_name="Термін (код/слово)")
    definition = models.TextField(verbose_name="Визначення / Пояснення")
    category = models.CharField(max_length=50, blank=True, default="Базові поняття", verbose_name="Категорія")

    class Meta:
        verbose_name = "Термін словника"
        verbose_name_plural = "Словник термінів"
        ordering = ['word']

    def __str__(self):
        return self.word
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    last_lesson = models.ForeignKey('Lesson', on_delete=models.SET_NULL, null=True, blank=True)
    # Додаємо це поле:
    lessons_completed = models.ManyToManyField('Lesson', related_name='completed_by', blank=True)

# Автоматичне створення профілю при реєстрації юзера
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)