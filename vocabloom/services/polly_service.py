import boto3
import base64
from django.conf import settings
from botocore.exceptions import BotoCoreError, ClientError
import logging

logger = logging.getLogger(__name__)


class PollyService:

    def __init__(self):
        self.polly_client = boto3.client(
            "polly",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

    def text_to_speech(self, text, voice_id="Joanna", output_format="mp3", speed="90%"):
        try:
            # Validate input
            if not text or not text.strip():
                return {"error": "Text cannot be empty"}

            logger.info(
                f"Converting text to speech: '{text[:50]}...' with voice {voice_id}"
            )

            ssml_text = f'<speak><prosody rate="{speed}">{text}</prosody></speak>'

            response = self.polly_client.synthesize_speech(
                Text=ssml_text, TextType="ssml", OutputFormat=output_format, VoiceId=voice_id
            )

            # Read audio stream
            audio_stream = response["AudioStream"].read()

            # Convert to base64 for easy transmission
            audio_base64 = base64.b64encode(audio_stream).decode("utf-8")

            return {
                "success": True,
                "audio_data": audio_base64,
                "content_type": f"audio/{output_format}",
            }

        except (BotoCoreError, ClientError) as error:
            logger.error(f"Polly error: {error}")
            return {"error": f"AWS Polly error: {str(error)}"}
        except Exception as error:
            logger.error(f"Unexpected error: {error}")
            return {"error": f"Unexpected error: {str(error)}"}
