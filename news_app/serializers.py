from rest_framework import serializers
from .models import Article, Publisher, Newsletter, CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer for the CustomUser model, exposing a limited set of
    fields.
    """
    class Meta:
        model = CustomUser
        fields = ['username']


class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for the Publisher model.
    """
    class Meta:
        model = Publisher
        fields = ['name']


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Article model, including nested author details.
    """
    article_author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'article_author']


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for the Newsletter model, including nested author
    details.
    """
    newsletter_author = CustomUserSerializer(read_only=True)

    class Meta:
        model = Newsletter
        fields = ['id', 'title', 'content', 'newsletter_author']
