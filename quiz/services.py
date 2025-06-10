from typing import Dict, Any
import openai
from django.conf import settings
import json
import os

class QuizGenerator:
    def __init__(self):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = "gpt-3.5-turbo"

    def generate_question(self, subject: str, topic: str, difficulty: str, class_level: str) -> Dict[str, Any]:
        """
        Generate a single quiz question using OpenAI's API.
        
        Args:
            subject (str): The subject (e.g., "Mathematics", "Physics")
            topic (str): The specific topic within the subject
            difficulty (str): The difficulty level (e.g., "easy", "medium", "hard")
            class_level (str): The class level (e.g., "SS1", "SS2", "SS3")
            
        Returns:
            Dict[str, Any]: A dictionary containing the question, options, correct answer, and explanation
        """
        prompt = f"""
        Generate a {difficulty} difficulty WAEC-style multiple choice question for {class_level} students.
        Subject: {subject}
        Topic: {topic}
        
        The question should:
        1. Be clear and concise
        2. Have exactly 4 options (A, B, C, D)
        3. Have only one correct answer
        4. Include a detailed explanation of the correct answer
        5. Be appropriate for {class_level} level
        6. Follow WAEC examination standards
        
        Format the response as a JSON object with the following structure:
        {{
            "question": "the question text",
            "options": {{
                "A": "option A",
                "B": "option B",
                "C": "option C",
                "D": "option D"
            }},
            "correct_answer": "the letter of the correct option (A, B, C, or D)",
            "explanation": "detailed explanation of why the answer is correct"
        }}
        """

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional WAEC examination question generator."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            # Extract and parse the JSON response
            content = response.choices[0].message.content
            question_data = json.loads(content)

            # Validate the response structure
            required_fields = ['question', 'options', 'correct_answer', 'explanation']
            if not all(field in question_data for field in required_fields):
                raise ValueError("Generated question is missing required fields")

            # Validate options
            if not all(option in question_data['options'] for option in ['A', 'B', 'C', 'D']):
                raise ValueError("Generated question must have exactly 4 options (A, B, C, D)")

            # Validate correct answer
            if question_data['correct_answer'] not in ['A', 'B', 'C', 'D']:
                raise ValueError("Correct answer must be one of: A, B, C, D")

            return question_data

        except Exception as e:
            # Log the error and raise a more specific exception
            print(f"Error generating question: {str(e)}")
            raise Exception(f"Failed to generate question: {str(e)}")

    def generate_questions_batch(self, subject: str, topic: str, difficulty: str, class_level: str, count: int) -> list:
        """
        Generate multiple quiz questions in a batch.
        
        Args:
            subject (str): The subject
            topic (str): The specific topic
            difficulty (str): The difficulty level
            class_level (str): The class level
            count (int): Number of questions to generate
            
        Returns:
            list: A list of question dictionaries
        """
        questions = []
        for _ in range(count):
            try:
                question = self.generate_question(subject, topic, difficulty, class_level)
                questions.append(question)
            except Exception as e:
                print(f"Error generating question in batch: {str(e)}")
                continue
        return questions 