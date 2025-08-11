from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, MagicMock
from ..services.polly_service import PollyService


class AudioTestCase(APITestCase):
    def setUp(self):
        """Set up test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        self.audio_url = reverse('text_to_speech')


    @patch('vocabloom.services.polly_service.boto3')
    def test_text_to_speech_success(self, mock_boto3):
        """Test successful text-to-speech conversion"""
        # Mock Polly response - Arrange
        mock_client = MagicMock()
        mock_response = {
            'AudioStream': MagicMock()
        }
        mock_response['AudioStream'].read.return_value = b'fake_audio_data'
        mock_client.synthesize_speech.return_value = mock_response
        mock_boto3.client.return_value = mock_client
        
        data = {
            'text': 'Hello world',
            'voice_id': 'Joanna'
        }

        # Act
        response = self.client.post(self.audio_url, data)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('audio_data', response.data)


    def test_text_to_speech_empty_text(self):
        """Test with empty text"""
        # Arrange
        data = {'text': ''}

        # Act
        response = self.client.post(self.audio_url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Text is required', response.data['error'])


    def test_text_to_speech_missing_text(self):
        """Test with missing text field"""
        # Arrange
        data = {'voice_id': 'Joanna'}

        # Act
        response = self.client.post(self.audio_url, data)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Text is required', response.data['error'])


    @patch('vocabloom.services.polly_service.boto3')
    def test_polly_service_error_handling(self, mock_boto3):
        """Test Polly service error handling"""
        # Arrange
        mock_client = MagicMock()
        mock_client.synthesize_speech.side_effect = Exception("AWS Error")
        mock_boto3.client.return_value = mock_client
        
        data = {'text': 'Test text'}

        # Act
        response = self.client.post(self.audio_url, data)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)