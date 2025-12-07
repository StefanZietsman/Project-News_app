from django.contrib import admin
from .models import Article, Publisher, Newsletter, CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Admin interface options for the CustomUser model.
    """
    list_display = ('username', 'email', 'role', 'publisher')
    list_filter = ('role',)
    search_fields = ('username', 'email')
    filter_horizontal = ('subscribed_journalists', 'subscribed_publishers')


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin interface options for the Article model.
    """
    list_display = (
        'title', 'article_author', 'editor_approved', 'independent_journalist')
    list_filter = ('editor_approved', 'independent_journalist')
    search_fields = ('title', 'content')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Admin interface options for the Newsletter model.
    """
    list_display = (
        'title', 'newsletter_author', 'editor_approved',
        'independent_journalist')
    list_filter = ('editor_approved', 'independent_journalist')
    search_fields = ('title', 'content')


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    """
    Admin interface options for the Publisher model.
    """
    list_display = ('name',)
    search_fields = ('name',)
