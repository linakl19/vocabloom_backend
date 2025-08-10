from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Tag, Word, Meaning, Definition, UserExample


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
        model = User
        fields = ["username", "email", "password", "first_name", "last_name"]

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
            username=validated_data["username"],
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]

    def validate_name(self, value):
        """Ensure tag name is unique per user"""
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            # Check if tag with this name already exists for this user
            existing_query = Tag.objects.filter(user=request.user, name=value)

            # If updating, exclude current instance
            if self.instance:
                existing_query = existing_query.exclude(pk=self.instance.pk)

            if existing_query.exists():
                raise serializers.ValidationError(
                    f"You already have a tag named '{value}'"
                )

        return value


class UserExampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserExample
        fields = ['id', 'example_text', 'created_at']
        read_only_fields = ['id', 'created_at']

    def validate_example_text(self, value):
        """Validate that example text is not empty"""
        if not value or not value.strip():
            raise serializers.ValidationError("Example text cannot be empty.")
        
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Example text must be at least 3 characters long.")
            
        return value.strip()


class DefinitionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Definition
        fields = ["id", "definition", "example"]
        extra_kwargs = {
            "definition": {"required": True},
            "example": {"required": False},
        }


class MeaningSerializer(serializers.ModelSerializer):
    definitions = DefinitionSerializer(many=True, required=False)

    class Meta:
        model = Meaning
        fields = ["id", "part_of_speech", "definitions"]


class WordSerializer(serializers.ModelSerializer):
    meanings = MeaningSerializer(many=True, required=False)
    user_examples = UserExampleSerializer(many=True, read_only=True)
    tag = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.none(), required=False, allow_null=True
    )

    class Meta:
        model = Word
        fields = [
            "id",
            "word",
            "phonetic",
            "audio",
            "note",
            "tag",
            "user_examples",
            "created_at",
            "meanings",
        ]
        extra_kwargs = {
            "word": {"required": True},
            "phonetic": {"required": False},
            "audio": {"required": False},
            "note": {"required": False},
            "created_at": {"read_only": True},
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            # Allow user's own tags + None
            self.fields["tag"].queryset = Tag.objects.filter(user=request.user)

    def validate(self, data):
        """Validate unique word per user"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            word_text = data.get('word')
            user = request.user

            # Check if word already exists for this user
            existing_query = Word.objects.filter(
                user=user,
                word__iexact=word_text  # Case-insensitive comparison
            )
            
            # If updating, exclude current instance
            if self.instance:
                existing_query = existing_query.exclude(pk=self.instance.pk)
            
            if existing_query.exists():
                raise serializers.ValidationError({
                    'word': f"You already have the word '{word_text}' in your vocabulary"
                })
        
        return data

    def validate_tag(self, value):
        """Validate tag belongs to current user (if provided)"""
        if value is None:
            return value  # Allow null tags

        request = self.context.get("request")
        if request and hasattr(request, "user"):
            if value.user != request.user:
                raise serializers.ValidationError("Tag does not belong to current user")

        return value

    def create(self, validated_data):
        meanings_data = validated_data.pop("meanings", [])
        word = Word.objects.create(**validated_data)

        for meaning_data in meanings_data:
            definitions_data = meaning_data.pop("definitions", [])
            meaning = Meaning.objects.create(word=word, **meaning_data)

            for definition_data in definitions_data:
                Definition.objects.create(meaning=meaning, **definition_data)

        return word

    def update(self, instance, validated_data):
        # Remove meanings from validated_data for now (don't update nested)
        validated_data.pop("meanings", None)

        # Update word fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance
