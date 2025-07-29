from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from ..models import Tag

class TagTestCase(APITestCase):
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

        self.tags_url = reverse('tags_list_create')
        self.tag_detail_url = lambda pk: reverse('tag_detail', kwargs={'pk': pk})

    # ----------- CREATE TAG TESTS -----------

    def test_create_new_tag_success(self):
        """User can create a new tag."""
        data = {"name": "Ada vocabulary"}
        response = self.client.post(self.tags_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Tag.objects.count(), 1)
        tag = Tag.objects.first()
        self.assertEqual(tag.name, 'Ada vocabulary')
        self.assertEqual(tag.user, self.user)
    
    def test_create_tag_returns_bad_request(self):
        """Returns 400 if name is missing."""
        data = {'name': ''}
        response = self.client.post(self.tags_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Tag.objects.count(), 0)

    # ----------- LIST TAGS -----------

    def test_list_user_tags_success(self):
        """Lists only tags for authenticated user."""
        Tag.objects.create(user=self.user, name='My Tag 1')
        Tag.objects.create(user=self.user, name='My Tag 2')
        Tag.objects.create(user=self.other_user, name='Not my tag')

        response = self.client.get(self.tags_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        tag_names = [tag['name'] for tag in response.data]
        self.assertIn('My Tag 1', tag_names)
        self.assertIn('My Tag 2', tag_names)
        self.assertNotIn('Not my tag', tag_names)

    # ----------- RETRIEVE TAGS -----------

    def test_invalid_user_tags_returns_not_found(self):
        """Cannot get details of another user's tag."""
        other_tag = Tag.objects.create(user=self.other_user, name='Other Tag')
        response = self.client.get(self.tag_detail_url(other_tag.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieves_one_tag_success(self):
        """Can retrieve own tag by id."""
        tag = Tag.objects.create(user=self.user, name='My Tag')
        response = self.client.get(self.tag_detail_url(tag.id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'My Tag')
        self.assertEqual(response.data['id'], tag.id)

    def test_retrieves_one_tag_returns_not_found(self):
        """Returns 404 if tag does not exist."""
        response = self.client.get(self.tag_detail_url(9))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ----------- UPDATE TAGS -----------

    def test_tag_update_with_put_success(self):
        """Can update a tag name with PUT."""
        tag = Tag.objects.create(user=self.user, name='Old tag name')
        data = {"name": "New name"}
        response = self.client.put(self.tag_detail_url(tag.id), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'New name')
        self.assertEqual(response.data['id'], tag.id)

    def test_tag_put_update_with_missing_data_returns_not_found(self):
        """PUT with missing data returns 400."""
        tag = Tag.objects.create(user=self.user, name='My tag')
        data = {"name": ""}
        response = self.client.put(self.tag_detail_url(tag.id), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_update_other_user_tag_forbidden(self):
        """Cannot update another user's tag."""
        other_tag = Tag.objects.create(user=self.other_user, name='Other Tag')
        data = {'name': 'Hacked Name'}
        response = self.client.patch(self.tag_detail_url(other_tag.id), data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        other_tag.refresh_from_db()
        self.assertEqual(other_tag.name, 'Other Tag')

    # ----------- DELETE TAGS -----------

    def test_delete_tag_success(self):
        """Can delete own tag."""
        tag = Tag.objects.create(user=self.user, name='To Delete')
        tag_id = tag.id
        response = self.client.delete(self.tag_detail_url(tag_id))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Tag.objects.filter(id=tag_id).exists())

    def test_delete_other_user_tag_forbidden(self):
        """Cannot delete another user's tag."""
        other_tag = Tag.objects.create(user=self.other_user, name='Other Tag')
        response = self.client.delete(self.tag_detail_url(other_tag.id))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Tag.objects.filter(id=other_tag.id).exists())
