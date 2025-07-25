from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Tag, Word, Meaning, Definition


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta: 
        model=User
        fields=['username', 'email', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class DefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Definition
        fields = ['id', 'definition', 'example']


class MeaningSerializer(serializers.ModelSerializer):
    definitions = DefinitionSerializer(many=True)

    class Meta:
        model = Meaning
        fields = ['id', 'part_of_speech', 'definitions']


class WordSerializer(serializers.ModelSerializer):
    meanings = MeaningSerializer(many=True)

    class Meta: 
        model = Word
        fields = [
            'id',
            'tag',
            'word',
            'phonetic',
            'audio',
            'note',
            'created_at',
            'meanings'
        ]
    
    def create(self, validated_data):
        meanings_data = validated_data.pop('meanings', [])
        word = Word.objects.create(**validated_data)
        for meaning_data in meanings_data:
            definitions_data = meaning_data.pop('definitions', [])
            meaning = Meaning.objects.create(word=word, **meaning_data)
            for definition_data in definitions_data:
                Definition.objects.create(meaning=meaning, **definition_data)
        return word

class WordBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model= Word
        fields=['id', 'word']
