from django.db import models


# Create your models here.
class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.first_name


class Tag(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tags')
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Word(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='words')
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True, related_name='words')
    word = models.CharField(max_length=100)
    phonetic = models.CharField(max_length=100, blank=True, null=True)
    audio_url = models.URLField(blank=True, null=True)
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.word


class Meaning(models.Model):
    word = models.ForeignKey(Word, on_delete=models.CASCADE, related_name='meanings')
    part_of_speech = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.part_of_speech or 'Meaning'} of {self.word.word}"


class Definition(models.Model):
    meaning = models.ForeignKey(Meaning, on_delete=models.CASCADE, related_name='definitions')
    definition = models.TextField()
    example = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.definition[:50]}{'...' if len(self.definition) > 50 else ''}"   