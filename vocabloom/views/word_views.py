from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema

from ..models import Tag, Word
from ..serializers import WordSerializer


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