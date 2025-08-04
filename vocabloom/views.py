from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from .models import Tag, Word
from .serializers import (
    TagSerializer,
    UserRegistrationSerializer,
    WordSerializer,
    SimpleSuccessSerializer,
    SimpleRefreshedSerializer,
    SimpleAuthenticatedSerializer
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# ===================================================
# AUTHENTICATION VIEWS
# ===================================================

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny] 

    @extend_schema(
        responses=SimpleSuccessSerializer,
        tags=['Authentication']
    )
        
    def post(self, request, *args, **kwargs):
        # Call parent method to get tokens
        response = super().post(request, *args, **kwargs)
        
        # If authentication failed, return the error response as-is
        if response.status_code != 200:
            return response
        
        # Extract tokens from parent response
        access_token = response.data.get('access')
        refresh_token = response.data.get('refresh')
        
        # Return tokens in response body for mobile compatibility
        response_data = {
            'access': access_token,
            'refresh': refresh_token,
            'success': True
        }
        res = Response(response_data)
        
        # Set environment-appropriate cookies
        cookie_secure = not settings.DEBUG
        cookie_samesite = 'None' if not settings.DEBUG else 'Lax'
        
        # Access token cookie
        res.set_cookie(
            key="access_token",
            value=access_token,
            max_age=60 * 60,  # 1 hour
            httponly=True,
            secure=cookie_secure,
            samesite=cookie_samesite,
            path='/'
        )
        
        # Refresh token cookie
        res.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=7 * 24 * 60 * 60,  # 7 days
            httponly=True,
            secure=cookie_secure,
            samesite=cookie_samesite,
            path='/'
        )
        
        return res

class CustomRefreshTokenView(TokenRefreshView):
    @extend_schema(
        responses=SimpleRefreshedSerializer,
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        try:
            refresh_token = request.COOKIES.get('refresh_token')
            request.data['refresh'] = refresh_token

            response = super().post(request, *args, **kwargs)
            tokens = response.data
            access_token = tokens['access']

            res = Response()

            res.data= {'refreshed': True}

            res.set_cookie(
                key="access_token", 
                value=access_token,
                httponly=True, 
                secure=True,
                samesite='None', 
                path='/'
            )

            return res
        
        except:
            return Response({'refreshed': False})

@extend_schema(responses=SimpleSuccessSerializer, tags=['Authentication'])
class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleSuccessSerializer

    def post(self, request):
        res = Response({'success': True})
        res.delete_cookie('access_token', path='/', samesite='None')
        res.delete_cookie('refresh_token', path='/', samesite='None')
        return res

@extend_schema(responses=SimpleAuthenticatedSerializer, tags=['Authentication'])
class IsAuthenticatedView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleAuthenticatedSerializer

    def get(self, request):
        return Response({'authenticated': True})
    def post(self, request):
        return Response({'authenticated': True})

@extend_schema(request=UserRegistrationSerializer, responses=UserRegistrationSerializer, tags=['Authentication'])
class RegisterUserView(views.APIView):
    permission_classes = [AllowAny]
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ===================================================
# TAG VIEWS
# ===================================================

@extend_schema(tags=['Tags'])
class TagListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

@extend_schema(tags=['Tags'])
class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)

# ===================================================
# WORD VIEWS
# ===================================================

@extend_schema(tags=['Words'])
class WordsByTagView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordSerializer

    def get_queryset(self):
        tag_id = self.kwargs['pk']
        user = self.request.user
        get_object_or_404(Tag, id=tag_id, user=user)
        return Word.objects.filter(tag__id=tag_id, user=user)

@extend_schema(tags=['Words'])
class WordListCreateView(generics.ListCreateAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=WordSerializer

    def get_queryset(self):
        return Word.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_serializer_context(self):
        """Ensure request is in serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

@extend_schema(tags=['Words'])
class WordDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class=WordSerializer

    def get_queryset(self):
        return Word.objects.filter(user=self.request.user)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        note_value = request.data.get('note', None)

        if note_value is None:
            return Response({'detail': 'PATCH must include a "note" field.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance, data={'note': note_value}, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

