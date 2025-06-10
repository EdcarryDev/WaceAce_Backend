from django.core.management.base import BaseCommand
from quiz.models import Subject, Topic, Quiz
from django.db import transaction
import random

class Command(BaseCommand):
    help = 'Generate WASSCE practice quizzes in three difficulty levels per topic'

    def get_wassce_duration(self, difficulty):
        """Return duration based on WASSCE practice difficulty"""
        durations = {
            'Easy': 10,    # Shorter duration for practice
            'Medium': 15,  # Standard WASSCE duration
            'Hard': 20     # Extended for challenging practice
        }
        return durations[difficulty]

    def get_wassce_class_level(self, difficulty):
        """Return appropriate class level based on difficulty"""
        levels = {
            'Easy': 'Grade 10',    # Foundational practice
            'Medium': 'Grade 11',  # Intermediate practice
            'Hard': 'Grade 12'     # WASSCE level practice
        }
        return levels[difficulty]

    def get_num_questions(self, difficulty):
        """Return number of questions based on difficulty"""
        question_ranges = {
            'Easy': (10),      # 10-20 questions for easy quizzes
            'Medium': (15),    # 20-30 questions for medium quizzes
            'Hard': (20)       # 30-40 questions for hard quizzes
        }
        return question_ranges[difficulty]

    def generate_quiz_title(self, subject_name, topic_name, difficulty):
        """Generate a WASSCE practice quiz title with difficulty"""
        return f"WASSCE Practice ({difficulty}) - {subject_name}: {topic_name}"

    def generate_description(self, subject_name, topic_name, difficulty, duration):
        """Generate a WASSCE-focused quiz description with difficulty context"""
        difficulty_desc = {
            'Easy': "foundational concepts and basic problem-solving. This preparatory level helps build your understanding of core topics.",
            'Medium': "standard WASSCE-level questions and typical examination patterns. This level matches the actual examination difficulty.",
            'Hard': "challenging problems and advanced concepts. This level helps you excel in the WASSCE examination."
        }
        
        return f"""WASSCE preparation quiz for {subject_name}, focusing on {topic_name}.
        This {difficulty.lower()}-level practice quiz covers {difficulty_desc[difficulty]}
        Time allocated: {duration} minutes.
        This quiz is designed to help you systematically prepare for your WASSCE examination."""

    def handle(self, *args, **options):
        topics = Topic.objects.all()
        difficulties = ['Easy', 'Medium', 'Hard']
        quizzes_created = 0
        
        if not topics.exists():
            self.stdout.write(self.style.ERROR('No topics found. Please run generate_topics first.'))
            return

        try:
            with transaction.atomic():
                for topic in topics:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'\nGenerating WASSCE practice quizzes for {topic.subject.name} - {topic.name}'
                        )
                    )
                    
                    # Create one quiz for each difficulty level
                    for difficulty in difficulties:
                        duration = self.get_wassce_duration(difficulty)
                        class_level = self.get_wassce_class_level(difficulty)
                        num_questions = self.get_num_questions(difficulty)
                        title = self.generate_quiz_title(topic.subject.name, topic.name, difficulty)
                        description = self.generate_description(topic.subject.name, topic.name, difficulty, duration)
                        
                        quiz = Quiz.objects.create(
                            title=title,
                            topic=topic,
                            class_level=class_level,
                            difficulty=difficulty,
                            duration_minutes=duration,
                            description=description,
                            num_of_questions=num_questions,
                            is_active=True,
                            is_wassce_related=True
                        )
                        
                        self.stdout.write(
                            self.style.SUCCESS(
                                f'    Created: {quiz.title} ({class_level}, {duration} mins, {num_questions} questions)'
                            )
                        )
                        quizzes_created += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f'\nSuccessfully created {quizzes_created} WASSCE practice quizzes!'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'- One quiz per difficulty level (Easy, Medium, Hard) for each topic'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'- {quizzes_created} total quizzes across {len(topics)} topics'
                )
            )
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating quizzes: {str(e)}'))
            raise 