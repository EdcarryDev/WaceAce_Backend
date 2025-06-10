from django.core.management.base import BaseCommand
from quiz.models import Subject, Topic, Quiz
from django.shortcuts import get_object_or_404
import requests
import json

class Command(BaseCommand):
    help = 'Test question generation endpoints'

    def handle(self, *args, **options):
        # 1. First make sure we have a subject and topic
        subject = get_object_or_404(Subject, name="Mathematics")
        topic = Topic.objects.filter(subject=subject).first()
        
        if not topic:
            self.stdout.write(self.style.ERROR('No topics found for Mathematics. Please run generate_topics first.'))
            return
            
        # 2. Create a test quiz
        quiz = Quiz.objects.create(
            title="Test Mathematics Quiz",
            subject=subject,
            topic=topic,
            class_level="Grade 10",
            difficulty="Medium",
            duration_minutes=30,
            description="Test quiz for question generation"
        )
        
        self.stdout.write(self.style.SUCCESS(f'Created test quiz: {quiz.title} (ID: {quiz.id})'))
        
        # 3. Test generating multiple questions
        self.stdout.write(self.style.SUCCESS('\nTesting multiple questions generation...'))
        try:
            response = requests.post(
                f'http://localhost:8000/api/quizzes/{quiz.id}/generate_questions/',
                json={'num_questions': 3}  # Let's generate 3 questions for testing
            )
            
            if response.status_code == 201:
                result = response.json()
                self.stdout.write(self.style.SUCCESS('Successfully generated multiple questions:'))
                for question in result['questions']:
                    self.stdout.write(f"\nQuestion: {question['question_text']}")
                    self.stdout.write(f"A: {question['option_a']}")
                    self.stdout.write(f"B: {question['option_b']}")
                    self.stdout.write(f"C: {question['option_c']}")
                    self.stdout.write(f"D: {question['option_d']}")
                    self.stdout.write(f"Correct Answer: {question['correct_answer']}")
            else:
                self.stdout.write(self.style.ERROR(f'Error: {response.text}'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error testing multiple questions: {str(e)}'))
        
        # 4. Test generating a single question
        self.stdout.write(self.style.SUCCESS('\nTesting single question generation...'))
        try:
            response = requests.post(
                'http://localhost:8000/api/questions/generate_for_quiz/',
                json={'quiz_id': quiz.id}
            )
            
            if response.status_code == 201:
                question = response.json()
                self.stdout.write(self.style.SUCCESS('Successfully generated single question:'))
                self.stdout.write(f"\nQuestion: {question['question_text']}")
                self.stdout.write(f"A: {question['option_a']}")
                self.stdout.write(f"B: {question['option_b']}")
                self.stdout.write(f"C: {question['option_c']}")
                self.stdout.write(f"D: {question['option_d']}")
                self.stdout.write(f"Correct Answer: {question['correct_answer']}")
            else:
                self.stdout.write(self.style.ERROR(f'Error: {response.text}'))
        
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error testing single question: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('\nTest completed!')) 