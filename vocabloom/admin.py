from django.contrib import admin
from .models import Tag, Word, Meaning, Definition, UserExample


# ===================================================
# TAG ADMIN
# ===================================================

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'word_count')
    list_filter = ('user',)
    search_fields = ('name', 'user__username')

    def word_count(self, obj):
        return obj.words.count()
    word_count.short_description = 'Words Count'


# ===================================================
# WORD ADMIN
# ===================================================

@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ('word', 'user', 'tag', 'phonetic', 'has_audio', 'meanings_count', 'examples_count', 'created_at')
    list_filter = ('user', 'tag', 'created_at')
    search_fields = ('word', 'user__username', 'phonetic')
    readonly_fields = ('created_at',)

    def has_audio(self, obj):
        return bool(obj.audio)
    has_audio.boolean = True
    has_audio.short_description = 'Has Audio'

    def meanings_count(self, obj):
        return obj.meanings.count()
    meanings_count.short_description = 'Meanings'

    def examples_count(self, obj):
        return obj.user_examples.count()
    examples_count.short_description = 'User Examples'


# ===================================================
# MEANING ADMIN
# ===================================================

@admin.register(Meaning)
class MeaningAdmin(admin.ModelAdmin):
    list_display = ('word', 'part_of_speech', 'definitions_count')
    list_filter = ('part_of_speech', 'word__user')
    search_fields = ('word__word', 'part_of_speech')

    def definitions_count(self, obj):
        return obj.definitions.count()
    definitions_count.short_description = 'Definitions'


# ===================================================
# DEFINITION ADMIN
# ===================================================

@admin.register(Definition)
class DefinitionAdmin(admin.ModelAdmin):
    list_display = ('meaning_word', 'definition_preview', 'has_example')
    list_filter = ('meaning__part_of_speech', 'meaning__word__user')
    search_fields = ('definition', 'example', 'meaning__word__word')

    def meaning_word(self, obj):
        return obj.meaning.word.word
    meaning_word.short_description = 'Word'

    def definition_preview(self, obj):
        return obj.definition[:100] + '...' if len(obj.definition) > 100 else obj.definition
    definition_preview.short_description = 'Definition'

    def has_example(self, obj):
        return bool(obj.example)
    has_example.boolean = True
    has_example.short_description = 'Has Example'


# ===================================================
# USER EXAMPLE ADMIN
# ===================================================

@admin.register(UserExample)
class UserExampleAdmin(admin.ModelAdmin):
    list_display = ('word', 'user', 'example_preview', 'created_at')
    list_filter = ('user', 'word__tag', 'created_at')
    search_fields = ('example_text', 'word__word', 'user__username')
    readonly_fields = ('created_at',)

    def example_preview(self, obj):
        return obj.example_text[:100] + '...' if len(obj.example_text) > 100 else obj.example_text
    example_preview.short_description = 'Example Text'