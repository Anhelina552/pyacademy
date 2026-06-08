import json

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import Lesson, Quiz, UserProgress, DictionaryTerm, Profile

def home(request):
    return render(request, 'courses/home.html')

@login_required(login_url='/auth/login/')  # ЗМІНЕНО ТУТ: додали /auth/
def lesson_detail(request, lesson_number):
    lesson = get_object_or_404(Lesson, number=lesson_number)

    # 1. ПЕРЕВІРКА ДОСТУПУ (якщо це не перший урок)
    if lesson.number > 1:
        prev_lesson_number = lesson.number - 1
        # Чи є запис про те, що попередній урок пройдено?
        has_access = UserProgress.objects.filter(
            user=request.user,
            lesson__number=prev_lesson_number,
            lesson__course=lesson.course
        ).exists()

        if not has_access:
            # Перенаправляємо на попередній урок, якщо цей ще заблоковано
            return redirect('lesson_detail', lesson_number=prev_lesson_number)

    # 2. Дані для тестів
    quizzes = Quiz.objects.filter(lesson=lesson).values(
        'question', 'option_a', 'option_b', 'option_v', 'option_g', 'correct_option'
    )
    quizzes_json = json.dumps(list(quizzes), ensure_ascii=False)

    # 3. Дані для навігації
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
        'all_lessons': all_lessons,  # Для відображення меню
        'completed_ids': completed_ids,  # Для перевірки "замків" у шаблоні
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
    # Логіка отримання уроків
    total_lessons = Lesson.objects.count()
    current_lesson = Lesson.objects.get(id=lesson_id)

    # Розрахунок відсотків
    progress_percentage = (current_lesson.number / total_lessons) * 100

    return render(request, 'lesson.html', {
        'lesson': current_lesson,
        'lesson_number': current_lesson.number,
        'total_lessons': total_lessons,
        'progress_percentage': progress_percentage
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