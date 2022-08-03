from django.contrib import admin

from .models import Article


# Register your models here.
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'author', 'status']
    list_filter = ['author', 'status']
