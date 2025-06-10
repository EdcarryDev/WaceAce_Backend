from django.db import models
from django.utils import timezone

# Create your models here.

class Subject(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Topic(models.Model):
    name = models.CharField(max_length=100)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='topics')
    
    def __str__(self):
        return self.name

class Quiz(models.Model):
    CLASS_LEVEL_CHOICES = [
        ('Grade 10', 'Grade 10'),
        ('Grade 11', 'Grade 11'),
        ('Grade 12', 'Grade 12'),
    ]
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]
    title = models.CharField(max_length=200)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='quizzes', null=True, blank=True)
    class_level = models.CharField(max_length=10, choices=CLASS_LEVEL_CHOICES)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    duration_minutes = models.PositiveIntegerField(default=60)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True)
    is_wassce_related = models.BooleanField(default=True)
    num_of_questions = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Quizzes"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.topic.name})"
    
    @property
    def question_count(self):
        return self.questions.count()

class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1)  # 'A', 'B', 'C', or 'D'
    explanation = models.TextField()
    is_ai_generated = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # expires_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.quiz.title} - {self.question_text[:50]}..."
    
    # def save(self, *args, **kwargs):
    #     if not self.expires_at:
    #         # Set expiration to 24 hours from creation
    #         self.expires_at = timezone.now() + timezone.timedelta(hours=24)
    #     super().save(*args, **kwargs)