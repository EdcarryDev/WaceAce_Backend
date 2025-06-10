from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from .models import Subject, Question, Quiz, Topic
from .serializers import SubjectSerializer, QuestionSerializer, QuizSerializer, TopicSerializer
from .services import QuizGenerator
from django.db import models
from django.shortcuts import get_object_or_404
import random

# Create your views here.

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'subject__name']
    ordering_fields = ['name']
    ordering = ['name']  # Default ordering

    def get_queryset(self):
        """
        Get the list of topics with optional subject filter
        """
        queryset = Topic.objects.all().select_related('subject')
        
        # Filter by subject if specified
        subject = self.request.query_params.get('subject')
        if subject:
            try:
                # Try to convert to integer for ID search
                subject_id = int(subject)
                queryset = queryset.filter(subject__id=subject_id)
            except ValueError:
                # If not an integer, search by name
                queryset = queryset.filter(subject__name__icontains=subject)
        
        return queryset

    @action(detail=False, methods=['get'])
    def by_subject(self, request):
        """
        Get all topics grouped by subject
        """
        try:
            # Get all subjects with their topics
            subjects = Subject.objects.prefetch_related('topics').all()
            
            # Prepare the response data
            response_data = []
            for subject in subjects:
                topics = subject.topics.all()
                topic_serializer = self.get_serializer(topics, many=True)
                
                response_data.append({
                    'subject': {
                        'id': subject.id,
                        'name': subject.name
                    },
                    'topics': topic_serializer.data
                })
            
            return Response(response_data)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'topic__name', 'topic__subject__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-created_at']  # Default ordering

    def get_queryset(self):
        """
        Get the list of quizzes with optional WASSCE filter
        """
        queryset = Quiz.objects.all().select_related('topic', 'topic__subject')
        
        # Filter by is_wassce_related if specified
        is_wassce = self.request.query_params.get('is_wassce')
        if is_wassce is not None:
            is_wassce = is_wassce.lower() == 'true'
            queryset = queryset.filter(is_wassce_related=is_wassce)
        
        return queryset

    @action(detail=False, methods=['get'])
    def random_wassce_quizzes(self, request):
        """
        Get 10 random WASSCE-related quizzes filtered by user's selected topics
        """
        try:
            # Get user's selected topics from their profile
            user_profile = request.user.profile
            selected_topics = user_profile.selected_topics

            if not selected_topics:
                return Response(
                    {'error': 'No topics selected. Please complete the onboarding process.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Start with base query for WASSCE quizzes
            wassce_quizzes = Quiz.objects.filter(
                is_wassce_related=True
            ).select_related('topic', 'topic__subject')

            # Build a Q object for topic filtering
            topic_filter = Q()
            for subject_name, topic_names in selected_topics.items():
                # Add OR conditions for each subject's topics
                subject_filter = Q(topic__subject__name=subject_name) & Q(topic__name__in=topic_names)
                topic_filter |= subject_filter

            # Apply the topic filter
            wassce_quizzes = wassce_quizzes.filter(topic_filter)
            
            # Get total count of filtered WASSCE quizzes
            total_count = wassce_quizzes.count()
            
            if total_count == 0:
                return Response(
                    {'error': 'No WASSCE quizzes available for your selected topics'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get up to 10 random quizzes
            random_count = min(10, total_count)
            random_quizzes = wassce_quizzes.order_by('?')[:random_count]
            
            serializer = self.get_serializer(random_quizzes, many=True)
            return Response({
                'quizzes': serializer.data,
                'total_wassce_quizzes': total_count,
                'fetched_count': random_count,
                'selected_topics': selected_topics  # Include selected topics in response for debugging
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def random_trivial_quizzes(self, request):
        """
        Get 10 random trivial quizzes filtered by user's selected topics
        """
        try:
            # Get user's selected topics from their profile
            user_profile = request.user.profile
            selected_topics = user_profile.selected_topics

            if not selected_topics:
                return Response(
                    {'error': 'No topics selected. Please complete the onboarding process.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Start with base query for trivial quizzes
            trivial_quizzes = Quiz.objects.filter(
                is_wassce_related=False
            ).select_related('topic', 'topic__subject')

            # Build a Q object for topic filtering
            topic_filter = Q()
            for subject_name, topic_names in selected_topics.items():
                # Add OR conditions for each subject's topics
                subject_filter = Q(topic__subject__name=subject_name) & Q(topic__name__in=topic_names)
                topic_filter |= subject_filter

            # Apply the topic filter
            trivial_quizzes = trivial_quizzes.filter(topic_filter)
            
            # Get total count of filtered trivial quizzes
            total_count = trivial_quizzes.count()
            
            if total_count == 0:
                return Response(
                    {'error': 'No trivial quizzes available for your selected topics'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get up to 10 random quizzes
            random_count = min(10, total_count)
            random_quizzes = trivial_quizzes.order_by('?')[:random_count]
            
            serializer = self.get_serializer(random_quizzes, many=True)
            return Response({
                'quizzes': serializer.data,
                'total_trivial_quizzes': total_count,
                'fetched_count': random_count,
                'selected_topics': selected_topics  # Include selected topics in response for debugging
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'])
    def random_mixed_quizzes(self, request):
        """
        Get 10 random quizzes mixed from both WASSCE and non-WASSCE quizzes.
        The mix will be approximately 60% WASSCE and 40% non-WASSCE quizzes.
        Quizzes are filtered by user's selected topics and additional search criteria.
        
        Query Parameters:
        - subject: Filter by subject name or ID
        - topic: Filter by topic name
        - search: Search in quiz title, topic name, or subject name
        - difficulty: Filter by difficulty level (easy, medium, hard)
        - class_level: Filter by class level (grade 10, grade 11, grade 12)
        """
        try:
            # Get user's selected topics from their profile
            user_profile = request.user.profile
            selected_topics = user_profile.selected_topics

            if not selected_topics:
                return Response(
                    {'error': 'No topics selected. Please complete the onboarding process.'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get all quizzes with related fields
            all_quizzes = Quiz.objects.all().select_related('topic', 'topic__subject')
            
            # Build topic filter from user's selected topics
            topic_filter = Q()
            for subject_name, topic_names in selected_topics.items():
                # Add OR conditions for each subject's topics
                subject_filter = Q(topic__subject__name=subject_name) & Q(topic__name__in=topic_names)
                topic_filter |= subject_filter

            # Apply the topic filter
            all_quizzes = all_quizzes.filter(topic_filter)
            
            # Apply search filters if provided
            subject = request.query_params.get('subject')
            topic = request.query_params.get('topic')
            search_query = request.query_params.get('search')
            difficulty = request.query_params.get('difficulty')
            class_level = request.query_params.get('class_level')
            
            # Filter by subject (accepts both name and ID)
            if subject:
                try:
                    # Try to convert to integer for ID search
                    subject_id = int(subject)
                    all_quizzes = all_quizzes.filter(topic__subject__id=subject_id)
                except ValueError:
                    # If not an integer, search by name
                    all_quizzes = all_quizzes.filter(topic__subject__name__icontains=subject)
            
            # Filter by topic
            if topic:
                all_quizzes = all_quizzes.filter(topic__name__icontains=topic)
            
            # Filter by difficulty
            if difficulty:
                difficulty = difficulty.lower()
                if difficulty in ['easy', 'medium', 'hard']:
                    all_quizzes = all_quizzes.filter(difficulty__iexact=difficulty)
            
            # Filter by class level
            if class_level:
                class_level = class_level.lower()
                valid_levels = ['grade 10', 'grade 11', 'grade 12']
                if class_level in valid_levels:
                    all_quizzes = all_quizzes.filter(class_level__iexact=class_level)
            
            # Apply general search
            if search_query:
                all_quizzes = all_quizzes.filter(
                    models.Q(title__icontains=search_query) |
                    models.Q(topic__name__icontains=search_query) |
                    models.Q(topic__subject__name__icontains=search_query)
                )
            
            # Get total counts after applying filters
            total_count = all_quizzes.count()
            wassce_count = all_quizzes.filter(is_wassce_related=True).count()
            trivial_count = total_count - wassce_count
            
            if total_count == 0:
                return Response({
                    'error': 'No quizzes found matching the search criteria',
                    'filters_applied': {
                        'subject': subject,
                        'topic': topic,
                        'search': search_query,
                        'difficulty': difficulty,
                        'class_level': class_level,
                        'selected_topics': selected_topics
                    }
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Calculate how many of each type to fetch
            # We'll try to get 6 WASSCE and 4 non-WASSCE quizzes
            wassce_to_fetch = min(6, wassce_count)
            trivial_to_fetch = min(4, trivial_count)
            
            # If we don't have enough of one type, adjust the other
            if wassce_to_fetch < 6:
                trivial_to_fetch = min(10 - wassce_to_fetch, trivial_count)
            elif trivial_to_fetch < 4:
                wassce_to_fetch = min(10 - trivial_to_fetch, wassce_count)
            
            # Fetch random WASSCE quizzes
            wassce_quizzes = all_quizzes.filter(
                is_wassce_related=True
            ).order_by('?')[:wassce_to_fetch]
            
            # Fetch random non-WASSCE quizzes
            trivial_quizzes = all_quizzes.filter(
                is_wassce_related=False
            ).order_by('?')[:trivial_to_fetch]
            
            # Combine and shuffle the results
            combined_quizzes = list(wassce_quizzes) + list(trivial_quizzes)
            random.shuffle(combined_quizzes)
            
            serializer = self.get_serializer(combined_quizzes, many=True)
            return Response({
                'quizzes': serializer.data,
                'total_quizzes': total_count,
                'wassce_quizzes': wassce_count,
                'trivial_quizzes': trivial_count,
                'fetched_count': len(combined_quizzes),
                'wassce_fetched': wassce_to_fetch,
                'trivial_fetched': trivial_to_fetch,
                'filters_applied': {
                    'subject': subject,
                    'topic': topic,
                    'search': search_query,
                    'difficulty': difficulty,
                    'class_level': class_level,
                    'selected_topics': selected_topics
                }
            })
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def list(self, request, *args, **kwargs):
        """
        Get list of quizzes with metadata
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Get counts for metadata
        total_quizzes = queryset.count()
        wassce_quizzes = queryset.filter(is_wassce_related=True).count()
        
        # Paginate results
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data.update({
                'metadata': {
                    'total_quizzes': total_quizzes,
                    'wassce_quizzes': wassce_quizzes
                }
            })
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'results': serializer.data,
            'metadata': {
                'total_quizzes': total_quizzes,
                'wassce_quizzes': wassce_quizzes
            }
        })
    
    @action(detail=True, methods=['get'])
    def question(self, request, pk=None):
        """
        Fetch random questions from the quiz.
        Query params:
        - count: Number of random questions to return (default: 1)
        """
        quiz = self.get_object()
        count = request.query_params.get('count', '1')
        
        try:
            # Validate count parameter
            count = int(count)
            if count < 1:
                return Response(
                    {'error': 'Count must be at least 1'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Get total available questions
            available_count = quiz.questions.count()
            if available_count == 0:
                return Response(
                    {'error': 'No questions available in this quiz'}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Adjust count if it exceeds available questions
            count = min(count, available_count)
            
            # Fetch random questions
            questions = quiz.questions.order_by('?')[:count]
            serializer = QuestionSerializer(questions, many=True)
            
            return Response({
                'questions': serializer.data,
                'total_questions': available_count,
                'fetched_count': len(serializer.data)
            })
            
        except ValueError:
            return Response(
                {'error': 'Count must be a valid number'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def generate_questions(self, request, pk=None):
        quiz = self.get_object()
        
        # Validate num_questions parameter
        try:
            num_questions = int(request.data.get('num_questions', 10))
            if num_questions <= 0:
                return Response(
                    {'error': 'num_questions must be a positive integer'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'num_questions must be a valid integer'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            if not quiz.topic:
                return Response(
                    {'error': 'Quiz must have a topic assigned to generate questions'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check existing questions count
            existing_questions_count = quiz.questions.count()
            
            # If we already have enough questions, return them
            if existing_questions_count >= num_questions:
                questions = quiz.questions.all()[:num_questions]
                serializer = QuestionSerializer(questions, many=True)
                return Response({
                    'message': f'Retrieved {len(questions)} existing questions',
                    'questions': serializer.data,
                    'source': 'existing'
                }, status=status.HTTP_200_OK)
            
            # Calculate how many new questions we need
            questions_needed = num_questions - existing_questions_count
                
            quiz_generator = QuizGenerator()
            generated_questions_data = []
            
            # Keep generating until we have exactly the requested number
            while len(generated_questions_data) < questions_needed:
                remaining = questions_needed - len(generated_questions_data)
                batch = quiz_generator.generate_questions(
                    subject=quiz.topic.subject.name,
                    topic=quiz.topic.name,
                    difficulty=quiz.difficulty,
                    class_level=quiz.class_level,
                    num_questions=remaining
                )
                generated_questions_data.extend(batch)
            
            # Ensure we don't exceed the requested number
            generated_questions_data = generated_questions_data[:questions_needed]
            
            # Set quiz as WASSCE related since we're generating WASSCE questions
            quiz.is_wassce_related = True
            quiz.save()
                    
            # Create questions in bulk
            questions_to_create = []
            for question_data in generated_questions_data:
                questions_to_create.append(
                    Question(
                        quiz=quiz,
                        question_text=question_data['question'],
                        option_a=question_data['options']['A'],
                        option_b=question_data['options']['B'],
                        option_c=question_data['options']['C'],
                        option_d=question_data['options']['D'],
                        correct_answer=question_data['correct_answer'],
                        explanation=question_data['explanation'],
                        is_ai_generated=True
                    )
                )
            
            # Bulk create the questions
            created_questions = Question.objects.bulk_create(questions_to_create)
            
            if len(created_questions) != questions_needed:
                return Response({
                    'error': f'Failed to generate exact number of new questions. Requested: {questions_needed}, Generated: {len(created_questions)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Combine existing and new questions
            all_questions = list(quiz.questions.all()[:existing_questions_count]) + list(created_questions)
            serializer = QuestionSerializer(all_questions, many=True)
            
            return Response({
                'message': f'Successfully retrieved {existing_questions_count} existing questions and generated {len(created_questions)} new questions',
                'questions': serializer.data,
                'source': 'mixed',
                'existing_count': existing_questions_count,
                'generated_count': len(created_questions)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def questions(self, request, pk=None):
        """Get all questions for a quiz"""
        quiz = self.get_object()
        questions = quiz.questions.all()
        serializer = QuestionSerializer(questions, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def generate_next_question(self, request, pk=None):
        """
        Generate a single question on-the-fly without storing in database.
        This is designed for real-time quiz progression.
        
        Request body:
        {
            "previous_questions": [
                {
                    "question": "previous question text",
                    "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
                    "correct_answer": "A"
                },
                // ... more previous questions if any
            ]
        }
        """
        quiz = self.get_object()
        
        try:
            if not quiz.topic:
                return Response(
                    {'error': 'Quiz must have a topic assigned to generate questions'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get previous questions from request
            previous_questions = request.data.get('previous_questions', [])
            
            # Create a prompt that includes previous questions to avoid duplicates
            previous_questions_text = ""
            if previous_questions:
                previous_questions_text = "\nPrevious questions:\n"
                for q in previous_questions:
                    previous_questions_text += f"- {q['question']}\n"

            # Initialize quiz generator
            quiz_generator = QuizGenerator()
            
            # Generate a single question
            question_data = quiz_generator.generate_question(
                subject=quiz.topic.subject.name,
                topic=quiz.topic.name,
                difficulty=quiz.difficulty,
                class_level=quiz.class_level
            )
            
            # Return the generated question directly
            return Response({
                'question': question_data['question'],
                'options': question_data['options'],
                'correct_answer': question_data['correct_answer'],
                'explanation': question_data['explanation']
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        return Question.objects.filter(
            models.Q(expires_at__isnull=True) | 
            models.Q(expires_at__gt=timezone.now())
        )
    
    @action(detail=False, methods=['post'])
    def generate_for_quiz(self, request):
        quiz_id = request.data.get('quiz_id')
        
        try:
            quiz = Quiz.objects.get(id=quiz_id)
        except Quiz.DoesNotExist:
            return Response(
                {'error': 'Quiz not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
            
        if not quiz.topic:
            return Response(
                {'error': 'Quiz must have a topic assigned to generate questions'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        quiz_generator = QuizGenerator()
        try:
            question_data = quiz_generator.generate_question(
                subject=quiz.topic.subject.name,
                topic=quiz.topic.name,
                difficulty=quiz.difficulty,
                class_level=quiz.class_level
            )
            
            # Create question
            question = Question.objects.create(
                quiz=quiz,
                question_text=question_data['question'],
                option_a=question_data['options']['A'],
                option_b=question_data['options']['B'],
                option_c=question_data['options']['C'],
                option_d=question_data['options']['D'],
                correct_answer=question_data['correct_answer'],
                explanation=question_data['explanation'],
                is_ai_generated=True
            )
            
            serializer = self.get_serializer(question)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
