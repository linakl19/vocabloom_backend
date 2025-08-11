from django.test import TestCase
from django.contrib.auth.models import User
from ..models import Tag, Word, UserExample

class ModelTestCase(TestCase):
    def test_tag_str_representation(self):
        """Test Tag __str__ method"""
        user = User.objects.create_user(username='test', password='pass')
        tag = Tag.objects.create(user=user, name='Test Tag')
        self.assertEqual(str(tag), 'Test Tag')

    def test_word_str_representation(self):
        """Test Word __str__ method"""
        user = User.objects.create_user(username='test', password='pass')
        word = Word.objects.create(user=user, word='algorithm')
        self.assertEqual(str(word), 'algorithm')

    def test_user_example_str_representation(self):
        """Test UserExample __str__ method"""
        user = User.objects.create_user(username='test', password='pass')
        word = Word.objects.create(user=user, word='test')
        example = UserExample.objects.create(
            user=user, 
            word=word, 
            example_text='This is a long example sentence for testing.'
        )
        expected = "Example for 'test': This is a long example sentence for testing...."
        self.assertEqual(str(example), expected)