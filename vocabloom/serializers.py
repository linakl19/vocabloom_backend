from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Tag, Word, Meaning, Definition


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'email', 'first_name', 'last_name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class DefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Definition
        fields = ['id', 'definition', 'example']


class MeaningSerializer(serializers.ModelSerializer):
    definitions = DefinitionSerializer(many=True, read_only=True)

    class Meta:
        model = Meaning
        fields = ['id', 'word', 'part_of_speech', 'definitions']


class WordSerializer(serializers.ModelSerializer):
    meanings = MeaningSerializer(many=True, read_only=True)

    class Meta: 
        model = Word
        fields = [
            'id',
            'tag',
            'word',
            'phonetic',
            'audio_url',
            'note',
            'created_at',
            'meanings'
        ]
