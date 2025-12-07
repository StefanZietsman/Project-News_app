from django.apps import AppConfig


class NewsAppConfig(AppConfig):
    """
    Configuration class for the news_app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news_app'
