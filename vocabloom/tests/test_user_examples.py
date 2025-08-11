from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import Tag, Word, UserExample

class UserExampleTestCase(APITestCase):
    def setUp(self):
        """Set up test data and authenticate user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Create test word
        self.word = Word.objects.create(
            user=self.user,
            word='programming'
        )
        
        self.other_word = Word.objects.create(
            user=self.other_user,
            word='secret'
        )
    
    def test_create_user_example_sucess(self):
        """User can create an example for a word"""
        # Arrange
        url = reverse('user-example-create', kwargs={'word_id': self.word.id})
        data = {'example_text': 'I love programming in Python.'}

        # Act
        response = self.client.post(url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserExample.objects.count(), 1)
        example = UserExample.objects.first()
        self.assertEqual(example.user, self.user)
        self.assertEqual(example.word, self.word)


    def test_create_example_for_other_user_word_forbidden(self):
        """Cannot create example for another user's word"""
        # Arrange
        url = reverse('user-example-create', kwargs={'word_id': self.other_word.id})
        data = {'example_text': 'Trying to hack this word.'}

        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(UserExample.objects.count(), 0)


    def test_create_example_empty_text_fails_returns_bad_request(self):
        """Cannot create example with empty text"""
        # Arrange
        url = reverse('user-example-create', kwargs={'word_id': self.word.id})
        data = {'example_text': ''}

        # Act
        response = self.client.post(url, data)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('example_text', response.data)


    def test_list_user_examples_for_word_success(self):
        """List examples for a specific word"""
        # Arrange
        UserExample.objects.create(
            user=self.user, 
            word=self.word, 
            example_text='First example'
        )
        UserExample.objects.create(
            user=self.user, 
            word=self.word, 
            example_text='Second example'
        )
        
        url = reverse('user-example-list', kwargs={'word_id': self.word.id})

        # Act
        response = self.client.get(url)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_update_user_example_success(self):
        """User can update their own example"""
        # Arrange
        example = UserExample.objects.create(
            user=self.user,
            word=self.word,
            example_text='Original example'
        )
        
        url = reverse('user-example-detail', kwargs={
            'word_id': self.word.id,
            'example_id': example.id
        })
        data = {'example_text': 'Updated example'}

        # Act
        response = self.client.put(url, data)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        example.refresh_from_db()
        self.assertEqual(example.example_text, 'Updated example')

    def test_delete_user_example_success(self):
        """User can delete their own example"""
        # Arrange
        example = UserExample.objects.create(
            user=self.user,
            word=self.word,
            example_text='To be deleted'
        )
        
        url = reverse('user-example-detail', kwargs={
            'word_id': self.word.id,
            'example_id': example.id
        })

        # Act
        response = self.client.delete(url)
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(UserExample.objects.filter(id=example.id).exists())