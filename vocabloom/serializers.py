from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Tag, Word, Meaning, Definition


class SimpleSuccessSerializer(serializers.Serializer):
    success = serializers.BooleanField()


class SimpleRefreshedSerializer(serializers.Serializer):
    refreshed = serializers.BooleanField()


class SimpleAuthenticatedSerializer(serializers.Serializer):
    authenticated = serializers.BooleanField()


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField(required=True)
    
    class Meta: 
        model=User
        fields=['username', 'email', 'password', 'first_name', 'last_name']
    
    def validate_username(self, value):
        """Ensure username is not empty and unique"""
        if not value.strip():
            raise serializers.ValidationError("Username cannot be empty")
        
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists")
        
        return value

    def validate_email(self, value):
        """Ensure email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists")
        return value
    
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
        extra_kwargs = {
            'definition': {'required': True},
            'example': {'required': False},
        }


class MeaningSerializer(serializers.ModelSerializer):
    definitions = DefinitionSerializer(many=True, required=False)

    class Meta:
        model = Meaning
        fields = ['id', 'part_of_speech', 'definitions']


class WordSerializer(serializers.ModelSerializer):
    meanings = MeaningSerializer(many=True, required=False)
    tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.none(),  
        required=False,  
        allow_null=True 
    )

    class Meta:
        model = Word
        fields = ['id', 'word', 'phonetic', 'audio', 'note', 'tag', 'meanings', 'created_at']
        extra_kwargs = {
            'word': {'required': True},
            'phonetic': {'required': False},
            'audio': {'required': False}, 
            'note': {'required': False},
            'created_at': {'read_only': True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            # Allow user's own tags + None
            self.fields['tag'].queryset = Tag.objects.filter(user=request.user)

    def validate_tag(self, value):
        """Validate tag belongs to current user (if provided)"""
        if value is None:
            return value  # Allow null tags
        
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            if value.user != request.user:
                raise serializers.ValidationError("Tag does not belong to current user")
        
        return value

    def create(self, validated_data):
        meanings_data = validated_data.pop('meanings', [])
        word = Word.objects.create(**validated_data)
        
        for meaning_data in meanings_data:
            definitions_data = meaning_data.pop('definitions', [])
            meaning = Meaning.objects.create(word=word, **meaning_data)
            
            for definition_data in definitions_data:
                Definition.objects.create(meaning=meaning, **definition_data)
        
        return word
    

    def update(self, instance, validated_data):
        # Remove meanings from validated_data for now (don't update nested)
        validated_data.pop('meanings', None)
        
        # Update word fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance
    

