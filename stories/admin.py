from django.contrib import admin
from .models import Story, Chapter, Audio, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author')
    search_fields = ('title', 'author')
    filter_horizontal = ('categories',)
    fields = ('title', 'author', 'description', 'cover', 'categories')


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('story', 'number', 'title')
    list_filter = ('story',)
    search_fields = ('title', 'content')
    ordering = ('story', 'number')


@admin.register(Audio)
class AudioAdmin(admin.ModelAdmin):
    list_display = ('id', 'chapter')
