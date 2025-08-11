from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema

from ..models import Word, UserExample
from ..serializers import UserExampleSerializer
from ..services.gemini_service import GeminiService


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
        
        context = request.data.get('context')
        difficulty_level = request.data.get('difficulty_level', 'intermediate')
        
        # Initialize Gemini service
        gemini_service = GeminiService()
        
        result = gemini_service.generate_user_example(
            word=word.word,
            context=context,
            difficulty_level=difficulty_level
        )
        
        if result.get('success'):
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_500_INTERNAL_SERVER_ERROR)