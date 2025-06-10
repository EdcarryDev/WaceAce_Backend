from rest_framework import serializers
from .models import Subject, Question, Quiz, Topic
from django.utils import timezone

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class TopicSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    
    class Meta:
        model = Topic
        fields = ['id', 'name', 'subject', 'subject_name']

class QuestionSerializer(serializers.ModelSerializer):    
    class Meta:
        model = Question
        fields = '__all__'
    
class QuizSerializer(serializers.ModelSerializer):
    question_count = serializers.CharField(source='num_of_questions', read_only=True)
    subject_name = serializers.CharField(source='topic.subject.name', read_only=True)
    topic_name = serializers.CharField(source='topic.name', read_only=True)
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'topic_name', 'class_level', 'difficulty', 
                 'duration_minutes', 'description', 'created_at', 'updated_at', 
                 'question_count', 'subject_name', 'is_wassce_related']
    
    def get_question_count(self, obj):
        return obj.questions.count()
