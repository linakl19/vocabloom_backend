from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from drf_spectacular.utils import extend_schema

from ..services.polly_service import PollyService


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