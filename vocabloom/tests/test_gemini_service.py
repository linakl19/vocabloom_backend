from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from ..models import Word
from ..services.gemini_service import GeminiService


class GeminiIntegrationTestCase(APITestCase):
    """
    Test cases for Gemini AI integration.
    Note: During testing I can expect console messages like "Failed to initialize Gemini: API Error"
    These are expected when testing error handling scenarios
    """
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.word = Word.objects.create(
            user=self.user,
            word='algorithm'
        )


    # Mock the Google Generative AI library to avoid real API calls during testing
    @patch('vocabloom.services.gemini_service.genai')
    def test_generate_example_success(self, mock_genai):
        """Test successful example generation"""
        # Arrange Mock Gemini response
        mock_model = MagicMock()
        mock_response = MagicMock()
        mock_response.text = "The algorithm solved the problem efficiently."
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model
        
        url = reverse('generate-word-example', kwargs={'word_id': self.word.id})
        data = {
            'context': 'computer science',
            'difficulty_level': 'intermediate'
        }

        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('algorithm', response.data['example'])


    # Mock the Gemini service to simulate API errors and test error handling
    # Note: Expected message in terminal: "Failed to initialize Gemini: API Error" in terminal
    @patch('vocabloom.services.gemini_service.genai')
    def test_generate_example_api_error(self, mock_genai):
        """Test handling of Gemini API errors"""
        # Arrange
        mock_genai.configure.side_effect = Exception("API Error")
        
        url = reverse('generate-word-example', kwargs={'word_id': self.word.id})
        data = {'difficulty_level': 'beginner'}

        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('error', response.data)


    def test_generate_example_nonexistent_word(self):
        """Test generating example for non-existent word"""
        # Arrange
        url = reverse('generate-word-example', kwargs={'word_id': 9999})
        data = {'difficulty_level': 'intermediate'}

        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn('Word not found', response.data['error'])


    @patch('vocabloom.services.gemini_service.genai')
    def test_gemini_service_initializes_with_model(self, mock_genai):
        """Test that GeminiService initializes with a model instance"""
        # Arrange - Act
        mock_model = MagicMock()
        mock_genai.configure.return_value = None
        mock_genai.GenerativeModel.return_value = mock_model
        
        service = GeminiService()
        
        # Assert
        self.assertIsNotNone(service)
        self.assertIsNotNone(service.model)
        mock_genai.configure.assert_called_once()
        mock_genai.GenerativeModel.assert_called_once_with(model_name='gemini-1.5-flash')