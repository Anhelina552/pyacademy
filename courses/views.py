import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import Lesson, Quiz, UserProgress, DictionaryTerm, Profile

def home(request):
    return render(request, 'courses/home.html')


import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Lesson, Quiz, UserProgress, Course  # перевір свої імпорти моделей


@login_required(login_url='/auth/login/')
def lesson_detail(request, lesson_number):
    # 1. ПЕРЕВІРКА НАЯВНОСТІ УРОКУ В БАЗІ
    # Шукаємо урок, якщо його взагалі немає в системі з таким номером
    lesson = Lesson.objects.filter(number=lesson_number).first()

    if not lesson:
        # Якщо уроку з таким номером немає, перевіримо, чи це спроба відкрити пустий курс
        # (Або якщо хочеш підстрахуватися, просто рендеримо сторінку розробки)
        return render(request, 'courses/course_under_development.html')

    # 2. ПЕРЕВІРКА КІЛЬКОСТІ УРОКІВ У ЦЬОМУ КУРСІ
    # Якщо курс існує, але в ньому випадково виявилося 0 уроків (на майбутнє)
    if lesson.course.lessons.count() == 0:
        return render(request, 'courses/course_under_development.html')

    # 3. ПЕРЕВІРКА ДОСТУПУ (якщо це не перший урок) — Твій оригінальний код
    if lesson.number > 1:
        prev_lesson_number = lesson.number - 1
        has_access = UserProgress.objects.filter(
            user=request.user,
            lesson__number=prev_lesson_number,
            lesson__course=lesson.course
        ).exists()

        if not has_access:
            return redirect('lesson_detail', lesson_number=prev_lesson_number)

    # 4. Дані для тестів
    quizzes = Quiz.objects.filter(lesson=lesson).values(
        'question', 'option_a', 'option_b', 'option_v', 'option_g', 'correct_option'
    )
    quizzes_json = json.dumps(list(quizzes), ensure_ascii=False)

    # 5. Дані для навігації
    all_lessons = Lesson.objects.filter(course=lesson.course).order_by('number')
    completed_ids = UserProgress.objects.filter(
        user=request.user,
        lesson__course=lesson.course
    ).values_list('lesson_id', flat=True)

    next_lesson = Lesson.objects.filter(
        course=lesson.course,
        number=lesson.number + 1
    ).first()

    return render(request, 'courses/lesson.html', {
        'lesson': lesson,
        'all_lessons': all_lessons,
        'completed_ids': completed_ids,
        'quizzes_json': quizzes_json,
        'next_lesson': next_lesson,
    })
@login_required(login_url='/auth/login/')  # Якщо не авторизований — перекине на вхід
def user_progress(request):
    # 1. Рахуємо загальну кількість уроків у системі
    total_lessons_count = Lesson.objects.count()

    # 2. Отримуємо всі уроки, які пройшов СУМЕЕ САМЕ ЦЕЙ користувач
    completed_progress = UserProgress.objects.filter(user=request.user)
    completed_lessons_count = completed_progress.count()

    # Витягуємо список ID пройдених уроків, щоб підсвічувати їх у списку тем
    completed_lesson_ids = completed_progress.values_list('lesson_id', flat=True)

    # 3. Рахуємо загальний відсоток проходження
    if total_lessons_count > 0:
        global_percentage = int((completed_lessons_count / total_lessons_count) * 100)
    else:
        global_percentage = 0

    # 4. Беремо всі уроки з бази, щоб динамічно вивести їх у списку модулів
    all_lessons = Lesson.objects.all().order_by('number')

    context = {
        'total_lessons_count': total_lessons_count,
        'completed_lessons_count': completed_lessons_count,
        'global_percentage': global_percentage,
        'all_lessons': all_lessons,
        'completed_lesson_ids': completed_lesson_ids,
    }

    return render(request, 'courses/progress.html', context)


@csrf_protect  # Захист від CSRF-атак (для диплома це жирний плюс за безпеку)
def complete_lesson(request, lesson_number):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            # Шукаємо урок за його номером
            lesson = Lesson.objects.get(number=lesson_number)

            # Створюємо запис про прогрес (get_or_create гарантує, що не буде дублів)
            progress, created = UserProgress.objects.get_or_create(
                user=request.user,
                lesson=lesson
            )

            return JsonResponse({'status': 'success', 'message': 'Прогрес збережено!'})
        except Lesson.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Урок не знайдено.'}, status=404)

    return JsonResponse({'status': 'error', 'message': 'Помилка запиту.'}, status=400)


def dictionary_view(request):
    # Отримуємо всі терміни, відсортовані за алфавітом
    terms = DictionaryTerm.objects.all()
    return render(request, 'courses/dictionary.html', {'terms': terms})


def lesson_view(request, lesson_id):
    # Використовуємо get_object_or_404, щоб сайт не «падав» з помилкою 500, якщо ID не існує
    current_lesson = get_object_or_404(Lesson, id=lesson_id)

    # Отримуємо курс, до якого належить цей урок
    current_course = current_lesson.course

    # Рахуємо кількість уроків ТІЛЬКИ для цього конкретного курсу
    total_lessons = Lesson.objects.filter(course=current_course).count()

    # Якщо уроків у курсі чомусь немає (захист від ділення на нуль)
    if total_lessons > 0:
        progress_percentage = (current_lesson.number / total_lessons) * 100
    else:
        progress_percentage = 0

    return render(request, 'lesson.html', {
        'lesson': current_lesson,
        'lesson_number': current_lesson.number,
        'total_lessons': total_lessons,
        'progress_percentage': int(progress_percentage)  # Перетворюємо в ціле число, щоб у CSS не було довгих дробів типу 33.3333%
    })


def course_home(request):
    if request.user.is_authenticated:
        # Створюємо профіль, якщо він ще не існує
        profile, created = Profile.objects.get_or_create(user=request.user)

        if profile.last_lesson:
            # Використовуємо lesson_number, як у твоєму urls.py
            return redirect('lesson_detail', lesson_number=profile.last_lesson.number)

    return render(request, 'course_list.html')


@login_required
def complete_lesson(request, lesson_number):
    # Отримуємо об'єкт уроку один раз (get_object_or_404 вже робить .get())
    lesson = get_object_or_404(Lesson, number=lesson_number)

    # Записуємо прогрес
    UserProgress.objects.get_or_create(user=request.user, lesson=lesson)

    # Оновлюємо "поточний" урок у профілі
    profile, created = Profile.objects.get_or_create(user=request.user)

    # Використовуємо .add() для ManyToManyField
    profile.lessons_completed.add(lesson)

    # Оновлюємо останній урок
    profile.last_lesson = lesson
    profile.save()

    # Перенаправляємо на наступний урок (якщо він є)
    # Важливо: використовуй фільтр, щоб знайти урок саме в тому ж курсі, якщо вони розділені
    next_lesson = Lesson.objects.filter(number__gt=lesson_number).order_by('number').first()

    if next_lesson:
        return redirect('lesson_detail', lesson_number=next_lesson.number)
    else:
        return redirect('home')
def course_development_view(request):
    return render(request, 'courses/course_under_development.html')