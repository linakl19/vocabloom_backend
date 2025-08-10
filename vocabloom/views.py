from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from rest_framework import generics, views, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from rest_framework.generics import GenericAPIView

from .services.polly_service import PollyService
from .services.gemini_service import GeminiService

from rest_framework.decorators import api_view, permission_classes

from .models import Tag, Word
from .models import UserExample
from .serializers import (
    TagSerializer,
    UserRegistrationSerializer,
    WordSerializer,
    UserExampleSerializer,
    SimpleSuccessSerializer,
    SimpleRefreshedSerializer,
    SimpleAuthenticatedSerializer,
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

    @extend_schema(responses=SimpleSuccessSerializer, tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        # Call parent method to get tokens
        response = super().post(request, *args, **kwargs)

        # If authentication failed, return the error response as-is
        if response.status_code != 200:
            return response

        # Extract tokens and return in response body only
        access_token = response.data.get("access")
        refresh_token = response.data.get("refresh")

        # Return tokens in response body (no cookies)
        return Response(
            {"access": access_token, "refresh": refresh_token, "success": True}
        )


class CustomRefreshTokenView(TokenRefreshView):
    permission_classes = [AllowAny]

    @extend_schema(responses=SimpleRefreshedSerializer, tags=["Authentication"])
    def post(self, request, *args, **kwargs):
        # Standard token refresh - expects refresh token in request body
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Return success indicator along with new tokens
            return Response(
                {
                    "access": response.data.get("access"),
                    "refresh": response.data.get(
                        "refresh", request.data.get("refresh")
                    ),
                    "refreshed": True,
                }
            )

        return Response({"refreshed": False}, status=response.status_code)


@extend_schema(responses=SimpleSuccessSerializer, tags=["Authentication"])
class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleSuccessSerializer

    def post(self, request):
        # With token-only auth, logout is handled on frontend
        # Backend just confirms the request was authenticated
        return Response({"success": True})


@extend_schema(responses=SimpleAuthenticatedSerializer, tags=["Authentication"])
class IsAuthenticatedView(views.APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SimpleAuthenticatedSerializer

    def get(self, request):
        return Response({"authenticated": True})

    def post(self, request):
        return Response({"authenticated": True})


@extend_schema(
    request=UserRegistrationSerializer,
    responses=UserRegistrationSerializer,
    tags=["Authentication"],
)
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


@extend_schema(tags=["Tags"])
class TagListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=["Tags"])
class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)


# ===================================================
# WORD VIEWS
# ===================================================


@extend_schema(tags=["Words"])
class WordsByTagView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordSerializer

    def get_queryset(self):
        tag_id = self.kwargs["pk"]
        user = self.request.user
        get_object_or_404(Tag, id=tag_id, user=user)
        return Word.objects.filter(tag__id=tag_id, user=user)


@extend_schema(tags=["Words"])
class WordListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordSerializer

    def get_queryset(self):
        return Word.objects.filter(user=self.request.user).prefetch_related('user_examples')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_context(self):
        """Ensure request is in serializer context"""
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


@extend_schema(tags=["Words"])
class WordDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WordSerializer

    def get_queryset(self):
        return Word.objects.filter(user=self.request.user).prefetch_related('user_examples')

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        if "note" not in request.data:
            return Response(
                {"detail": 'PATCH must include a "note" field.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        note_value = request.data.get("note", None)

        serializer = self.get_serializer(
            instance, data={"note": note_value}, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


# ===================================================
# AUDIO VIEWS
# ===================================================


@extend_schema(
    request={
        "application/json": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to convert to speech"},
                "voice_id": {
                    "type": "string",
                    "description": "Voice ID (default: Joanna)",
                },
            },
            "required": ["text"],
        }
    },
    responses={
        200: {
            "type": "object",
            "properties": {
                "success": {"type": "boolean"},
                "audio_data": {"type": "string", "description": "Base64 encoded audio"},
                "content_type": {"type": "string"},
                "voice_id": {"type": "string"},
            },
        },
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
    tags=["Audio"],
)
class TextToSpeechView(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Convert text to speech using Amazon Polly"""
        text = request.data.get("text", "").strip()
        voice_id = request.data.get("voice_id", "Joanna")

        if not text:
            return Response(
                {"error": "Text is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        polly_service = PollyService()
        result = polly_service.text_to_speech(text, voice_id)

        if "error" in result:
            return Response(
                {"error": result["error"]}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response(result, status=status.HTTP_200_OK)


# ===================================================
# USER EXAMPLE VIEWS
# ===================================================


@extend_schema(
    request=UserExampleSerializer,
    responses={201: UserExampleSerializer},
    tags=["User Examples"],
)
class UserExampleCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserExampleSerializer

    def perform_create(self, serializer):
        word_id = self.kwargs["word_id"]
        word = get_object_or_404(Word, id=word_id, user=self.request.user)
        serializer.save(word=word, user=self.request.user)


@extend_schema(
    responses={200: UserExampleSerializer(many=True)}, tags=["User Examples"]
)
class UserExampleListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserExampleSerializer

    def get_queryset(self):
        word_id = self.kwargs["word_id"]
        word = get_object_or_404(Word, id=word_id, user=self.request.user)
        return UserExample.objects.filter(word=word, user=self.request.user).order_by("-created_at")


@extend_schema(
    request=UserExampleSerializer,
    responses={200: UserExampleSerializer},
    tags=["User Examples"],
)
class UserExampleDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserExampleSerializer
    lookup_url_kwarg = "example_id"

    def get_queryset(self):
        word_id = self.kwargs["word_id"]
        word = get_object_or_404(Word, id=word_id, user=self.request.user)
        return UserExample.objects.filter(word=word, user=self.request.user)


# ===================================================
# GEMINI AI VIEWS (Class-Based)
# ===================================================


@extend_schema(
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'context': {'type': 'string', 'description': 'Optional context'},
                'difficulty_level': {'type': 'string', 'enum': ['beginner', 'intermediate', 'advanced']},
            }
        }
    },
    responses={200: {'type': 'object'}},
    tags=['User Examples']
)
class GenerateWordExampleView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, word_id, *args, **kwargs):
        """Generate an example sentence for a word using Gemini AI"""
        try:
            word = Word.objects.get(id=word_id, user=request.user)
        except Word.DoesNotExist:
            return Response({
                'error': 'Word not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get parameters from request
        context = request.data.get('context')
        difficulty_level = request.data.get('difficulty_level', 'intermediate')
        
        # Initialize Gemini service
        gemini_service = GeminiService()
        
        # Generate single example
        result = gemini_service.generate_user_example(
            word=word.word,
            context=context,
            difficulty_level=difficulty_level
        )
        
        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
