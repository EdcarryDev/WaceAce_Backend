from django.test import TestCase
from ..services import QuizGenerator
import json

class OpenAIConnectionTest(TestCase):
    def setUp(self):
        self.quiz_generator = QuizGenerator()

    def test_openai_connection(self):
        """Test if we can successfully connect to OpenAI and generate a response"""
        try:
            # Test with a simple subject
            response = self.quiz_generator.generate_question("Basic Mathematics")
            
            # Check if response is properly formatted
            self.assertIsInstance(response, dict)
            self.assertIn('question', response)
            self.assertIn('options', response)
            self.assertIn('correct_answer', response)
            self.assertIn('explanation', response)
            
            # Check if options contain A, B, C, D
            self.assertIn('A', response['options'])
            self.assertIn('B', response['options'])
            self.assertIn('C', response['options'])
            self.assertIn('D', response['options'])
            
            # Check if correct_answer is valid
            self.assertIn(response['correct_answer'], ['A', 'B', 'C', 'D'])
            
            print("\nSuccessfully generated question:")
            print(f"Question: {response['question']}")
            print("Options:")
            for key, value in response['options'].items():
                print(f"{key}: {value}")
            print(f"Correct Answer: {response['correct_answer']}")
            print(f"Explanation: {response['explanation']}")
            
        except Exception as e:
            self.fail(f"OpenAI connection failed with error: {str(e)}") 