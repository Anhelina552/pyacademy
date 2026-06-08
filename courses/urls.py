from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Ваша перша сторінка
    path('lesson/<int:lesson_number>/', views.lesson_detail, name='lesson_detail'), # Друга сторінка
    path('dictionary/', views.dictionary_view, name='dictionary'),
    path('progress/', views.user_progress, name='progress'),
    path('lesson/<int:lesson_number>/complete/', views.complete_lesson, name='complete_lesson'),
]