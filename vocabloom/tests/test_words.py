from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import Tag, Word, Meaning, Definition


# Add this to your existing tests.py file
class WordTestCase(APITestCase):
    def setUp(self):
        """Set up test data and authenticate user"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        # Create another user for isolation testing
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        
        # Create tags
        self.movies_tag = Tag.objects.create(user=self.user, name='Movies')
        self.tech_tag = Tag.objects.create(user=self.user, name='Tech')
        self.other_user_tag = Tag.objects.create(user=self.other_user, name='Other Tag')
        
        # URL endpoints
        self.words_url = reverse('words_list_create')
        self.word_detail_url = lambda pk: reverse('word_detail', kwargs={'pk': pk})
        self.words_by_tag_url = lambda pk: reverse('words_by_tag', kwargs={'pk': pk})

    # ----------- CREATE WORD TESTS -----------

    def test_create_word_without_meanings_success(self):
        """Can create a word without meanings."""
        # Arrange
        data = {
            'tag': self.movies_tag.id,
            'word': 'cinematography',
            'phonetic': '/ˌsɪnəməˈtɒɡrəfi/',
            'audio': 'https://example.com/cinematography.mp3',
            'note': 'The art of making motion pictures',
        }

        # Act
        response = self.client.post(self.words_url, data, format='json')

        # Arrange
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Word.objects.count(), 1)
        word = Word.objects.first()
        self.assertEqual(word.word, 'cinematography')
        self.assertEqual(word.user, self.user)
        self.assertEqual(word.tag, self.movies_tag)
        self.assertEqual(word.phonetic, '/ˌsɪnəməˈtɒɡrəfi/')
        self.assertEqual(word.note, 'The art of making motion pictures')


    def test_create_tech_word_with_nested_meanings_success(self):
        """Can create a word with nested meanings and definitions."""
        # Arrange
        data = {
            'tag': self.tech_tag.id,
            'word': 'algorithm',
            'phonetic': '/ˈælɡərɪðəm/',
            'note': 'Fundamental programming concept',
            'meanings': [
                {
                    'part_of_speech': 'noun',
                    'definitions': [
                        {
                            'definition': 'A step-by-step procedure for calculations',
                            'example': 'The sorting algorithm improved performance significantly.'
                        },
                        {
                            'definition': 'A set of rules for solving problems',
                            'example': 'Machine learning algorithms can recognize patterns.'
                        }
                    ]
                }
            ]
        }
        # Act
        response = self.client.post(self.words_url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        word = Word.objects.first()
        self.assertEqual(word.word, 'algorithm')
        self.assertEqual(word.tag, self.tech_tag)
        self.assertEqual(word.meanings.count(), 1)
        meaning = word.meanings.first()
        self.assertEqual(meaning.part_of_speech, 'noun')
        self.assertEqual(meaning.definitions.count(), 2)
        definition = meaning.definitions.first()
        self.assertIn('step-by-step procedure', definition.definition)
        self.assertIn('sorting algorithm', definition.example)


    def test_create_movie_word_missing_data_returns_bad_request(self):
        """Returns 400 if required data is missing."""
        # Arrange
        data = {
            'tag': self.movies_tag.id,
            'word': '',
            'phonetic': '/test/',
        }
        # Act
        response = self.client.post(self.words_url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Word.objects.count(), 0)


    def test_create_word_without_tag_success(self):
        """Can create a word without a tag."""
        # Arrange
        data = {
            'word': 'untagged_word',
            'note': 'This word has no category',
        }
        # Act
        response = self.client.post(self.words_url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        word = Word.objects.first()
        self.assertEqual(word.word, 'untagged_word')
        self.assertIsNone(word.tag)


    def test_create_word_with_other_user_tag_returns_bad_request(self):
        """Cannot create a word using another user's tag."""
        # Arrange
        data = {
            'tag': self.other_user_tag.id,
            'word': 'hack_attempt',
        }
        # Act
        response = self.client.post(self.words_url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_movie_word_with_multiple_meanings(self):
        """Can create a word with multiple meanings."""
        # Arrange
        data = {
            'tag': self.movies_tag.id,
            'word': 'cut',
            'meanings': [
                {
                    'part_of_speech': 'noun',
                    'definitions': [
                        {
                            'definition': 'An edited version of a film',
                            'example': 'The director\'s cut was much longer.'
                        }
                    ]
                },
                {
                    'part_of_speech': 'verb',
                    'definitions': [
                        {
                            'definition': 'To edit or remove scenes from a film',
                            'example': 'They had to cut several scenes for time.'
                        }
                    ]
                }
            ]
        }
        # Act
        response = self.client.post(self.words_url, data, format='json')

        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        word = Word.objects.first()
        self.assertEqual(word.meanings.count(), 2)
        noun_meaning = word.meanings.filter(part_of_speech='noun').first()
        self.assertIsNotNone(noun_meaning)
        self.assertIn('edited version', noun_meaning.definitions.first().definition)
        verb_meaning = word.meanings.filter(part_of_speech='verb').first()
        self.assertIsNotNone(verb_meaning)
        self.assertIn('edit or remove', verb_meaning.definitions.first().definition)


    # ----------- LIST, RETRIEVE, and FILTER WORDS -----------
    def test_list_user_words_only_success(self):
        """List words only for the authenticated user."""
        # Arrange
        Word.objects.create(user=self.user, tag=self.movies_tag, word='director')
        Word.objects.create(user=self.user, tag=self.tech_tag, word='framework')
        Word.objects.create(user=self.other_user, tag=self.other_user_tag, word='secret')

        # Act
        response = self.client.get(self.words_url)

        # Arrange
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        word_texts = [word['word'] for word in response.data]
        self.assertIn('director', word_texts)
        self.assertIn('framework', word_texts)
        self.assertNotIn('secret', word_texts)


    def test_retrieve_one_word_success(self):
        """Retrieve a single word by id."""
        # Arrange
        word = Word.objects.create(
            user=self.user,
            tag=self.tech_tag,
            word='blockchain',
            phonetic='/ˈblɒktʃeɪn/',
            note='Distributed ledger technology'
        )
        # Act
        response = self.client.get(self.word_detail_url(word.id))

        # Arrange
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['word'], 'blockchain')
        self.assertEqual(response.data['id'], word.id)
        self.assertEqual(response.data['note'], 'Distributed ledger technology')


    def test_words_by_movies_tag_filtering_success(self):
        """Filter words by tag (movies)."""
        # Arrange
        Word.objects.create(user=self.user, tag=self.movies_tag, word='protagonist')
        Word.objects.create(user=self.user, tag=self.movies_tag, word='antagonist')
        Word.objects.create(user=self.user, tag=self.tech_tag, word='deployment')

        # Act
        response = self.client.get(self.words_by_tag_url(self.movies_tag.id))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        word_texts = [word['word'] for word in response.data]
        self.assertIn('protagonist', word_texts)
        self.assertIn('antagonist', word_texts)
        self.assertNotIn('deployment', word_texts)


    # ----------- UPDATE WORDS -----------

    def test_update_word_note_only_patch_success(self):
        """Update only the note field with PATCH."""
        # Arrange
        word = Word.objects.create(
            user=self.user,
            tag=self.movies_tag,
            word='screenplay',
            note='old note about screenplay'
        )
        data = {'note': 'updated note: script for a movie or TV show'}

        # Act
        response = self.client.patch(self.word_detail_url(word.id), data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        word.refresh_from_db()
        self.assertEqual(word.note, 'updated note: script for a movie or TV show')


    def test_patch_without_note_returns_bad_request(self):
        """PATCH without note field returns 400."""
        # Arrange
        word = Word.objects.create(
            user=self.user,
            tag=self.tech_tag,
            word='database'
        )
        data = {'word': 'changed word'}

        # Act
        response = self.client.patch(self.word_detail_url(word.id), data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('note', response.data['detail'])


    # ----------- DELETE AND PERMISSIONS -----------
    def test_delete_word_success(self):
        """Delete a word by id."""
        # Arrange
        word = Word.objects.create(
            user=self.user,
            tag=self.movies_tag,
            word='storyboard'
        )
        word_id = word.id

        # Act
        response = self.client.delete(self.word_detail_url(word_id))

        # Assert
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Word.objects.filter(id=word_id).exists())


    def test_user_cannot_access_other_user_words_returns_not_found(self):
        """Cannot retrieve or delete another user's word."""
        # Arrange
        other_word = Word.objects.create(
            user=self.other_user,
            tag=self.other_user_tag,
            word='private_word'
        )
        # Act - Assert
        response = self.client.get(self.word_detail_url(other_word.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        response = self.client.delete(self.word_detail_url(other_word.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Word.objects.filter(id=other_word.id).exists())


    # ----------- AUTHENTICATION TESTS -----------

    def test_unauthenticated_access_returns_unauthorized(self):
        """All endpoints should require authentication."""
        # Arrange
        self.client.force_authenticate(user=None)

        # Act - Assert
        response = self.client.get(self.words_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        response = self.client.post(self.words_url, {'word': 'test'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
