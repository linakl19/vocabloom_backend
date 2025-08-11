from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

class AuthenticationTestCase(APITestCase):
    def setUp(self):
        """Set up URLs for authentication endpoints."""
        self.register_url = reverse('register_user')
        self.login_url = reverse('token_obtain_pair')
        self.logout_url = reverse('logout')
        self.auth_check_url = reverse('is_authenticated')

    # ----------- REGISTRATION TESTS -----------

    def test_user_registration(self):
        """Test user can register successfully."""
        # Arrange
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        # Act
        response = self.client.post(self.register_url, data)
        # Assert
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_registration_duplicate_email_returns_bad_request(self):
        """Prevent duplicate emails."""
        # Arrange
        User.objects.create_user(username='user1', email='test@example.com', password='pass123')
        data = {
            'username': 'user2',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        # Act
        response = self.client.post(self.register_url, data)
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_registration_invalid_data_returns_bad_request(self):
        """Test registration with invalid data returns 400."""
        # Arrange
        data = {
            'username': '',
            'email': 'invalid-email',
            'password': '123',
        }
        # Act
        response = self.client.post(self.register_url, data)
        # Assert
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    # ----------- LOGIN TESTS -----------
    def test_user_login_with_token(self):
        """Test user can login and use JWT token for authentication."""
        # Arrange
        User.objects.create_user(username='testuser', password='testpass123')
        data = {'username': 'testuser', 'password': 'testpass123'}
        # Act
        response = self.client.post(self.login_url, data)

        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data.get('access')
        self.assertIsNotNone(access_token)

        # Use token to access a protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        protected_response = self.client.get(self.auth_check_url)
        self.assertEqual(protected_response.status_code, status.HTTP_200_OK)
        self.assertTrue(protected_response.data['authenticated'])


    def test_login_invalid_credentials_returns_unauthorized(self):
        """Wrong password should fail."""
        # Arrange
        User.objects.create_user(username='testuser', password='correctpass')
        data = {'username': 'testuser', 'password': 'wrongpass'}
        # Act
        response = self.client.post(self.login_url, data)
        # Arrange
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)
        

    # ----------- LOGOUT TESTS -----------
    def test_logout_success(self):
        """Test authenticated user can logout."""
        # Arrange
        user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.force_authenticate(user=user)
        # Act
        response = self.client.post(self.logout_url)
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])


    def test_logout_unauthenticated_fails(self):
        """Unauthenticated users cannot logout."""
        # Act
        response = self.client.post(self.logout_url)
        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    # ----------- TOKEN REFRESH TESTS -----------
    def test_token_refresh_success(self):
        """Test token refresh functionality."""
        # Arrange
        user = User.objects.create_user(username='testuser', password='testpass123')
        
            # Get initial tokens
        login_data = {'username': 'testuser', 'password': 'testpass123'}
        login_response = self.client.post(self.login_url, login_data)
        refresh_token = login_response.data['refresh']
        
            # Test refresh
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': refresh_token}

        # Act 
        refresh_response = self.client.post(refresh_url, refresh_data)
        # Assert
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
        self.assertTrue(refresh_response.data['refreshed'])

    def test_token_refresh_invalid_token_fails(self):
        """Invalid refresh token should fail."""
        # Arrange
        refresh_url = reverse('token_refresh')
        refresh_data = {'refresh': 'invalid_token'}
        # Act
        response = self.client.post(refresh_url, refresh_data)
        # Assert
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    # ----------- COMPLETE FLOW -----------
    def test_complete_authentication_flow(self):
        """Test full auth flow: register -> login -> access protected endpoint -> logout."""
        # Register
        register_data = {
            'username': 'flowuser',
            'email': 'flow@example.com',
            'password': 'flowpass123',
            'first_name': 'Flow',
            'last_name': 'User'
        }
        register_response = self.client.post(self.register_url, register_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        
        # Login
        login_data = {'username': 'flowuser', 'password': 'flowpass123'}
        login_response = self.client.post(self.login_url, login_data)
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        # Access protected endpoint
        user = User.objects.get(username='flowuser')
        self.client.force_authenticate(user=user)
        auth_response = self.client.get(self.auth_check_url)
        self.assertEqual(auth_response.status_code, status.HTTP_200_OK)
        self.assertTrue(auth_response.data['authenticated'])
        
        # Logout
        logout_response = self.client.post(self.logout_url)
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
