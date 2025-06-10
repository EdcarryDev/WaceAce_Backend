from django.contrib import admin
from .models import Subject, Topic, Quiz, Question

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'subject']
    list_filter = ['subject']
    search_fields = ['name']

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'topic', 'class_level', 'difficulty', 'duration_minutes', 'is_active']
    list_filter = ['topic', 'class_level', 'difficulty', 'is_active']
    search_fields = ['title', 'description']

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'correct_answer', 'created_at']
    list_filter = ['quiz', 'created_at']
    search_fields = ['question_text']
