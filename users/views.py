from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages


def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # 1. Перевірка на порожні поля (базова валідація)
        if not username or not email or not password:
            messages.error(request, 'Будь ласка, заповніть всі поля!')
            return render(request, 'users/register.html')

        # 2. Перевірка на існування логіна
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Користувач з таким логіном вже існує!')
            return render(request, 'users/register.html')

        # 3. Перевірка на існування email
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Користувач з таким email вже зареєстрований!')
            return render(request, 'users/register.html')

        # 4. Створення користувача
        user = User.objects.create_user(username=username, email=email, password=password)

        login(request, user)
        messages.success(request, 'Реєстрація успішна!')
        return redirect('/')

    return render(request, 'users/register.html')

def login_view(request):
    if request.method == 'POST':
        # Тепер у полі логіна користувач вводить свій email
        email_input = request.POST.get('username')
        password = request.POST.get('password')

        # 1. Шукаємо користувача в базі даних за його email
        try:
            user_obj = User.objects.get(email=email_input)
            # Якщо знайшли, беремо його системний username
            username = user_obj.username
        except User.DoesNotExist:
            # Якщо користувача з таким email немає, підставляємо сам email,
            # щоб функція authenticate далі відпрацювала і повернула помилку
            username = email_input

        # 2. Перевіряємо пароль за допомогою системного username
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, 'Раді поверненню!')
            return redirect('/')
        else:
            messages.error(request, 'Неправильний email або пароль.')

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('/')