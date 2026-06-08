from django.contrib import admin
from .models import Course, Lesson, LessonBlock, Term, Quiz

# Налаштування інлайну для блоків контенту всередині уроку
from django.contrib import admin
from .models import Course, Lesson, LessonBlock, Term, Quiz


from django.contrib import admin
from .models import Course, Lesson, LessonBlock, Term, Quiz, DictionaryTerm

class LessonBlockInline(admin.StackedInline): # Перемкнули на StackedInline для більшої краси
    model = LessonBlock
    extra = 1
    fieldsets = [
        ('Візуальне оформлення блоку', {'fields': ['order', 'block_layout']}),
        ('Вміст текстового блоку', {'fields': ['block_title', 'block_text', 'block_image']}),
    ]

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['number', 'title']
    inlines = [LessonBlockInline]

admin.site.register(Course)
admin.site.register(Term)
admin.site.register(Quiz)

@admin.register(DictionaryTerm)
class DictionaryTermAdmin(admin.ModelAdmin):
    list_display = ('word', 'category')
    search_fields = ('word', 'definition')
    list_filter = ('category',)
