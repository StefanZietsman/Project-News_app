from django.db import models
from django.contrib.auth.models import AbstractUser


class Publisher(models.Model):
    """
    Represents a publishing house or company.
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    """
    Custom user model extending Django's AbstractUser.
    Includes roles (Reader, Journalist, Editor) and fields for
    subscriptions to journalists and publishers.
    """
    ROLE_CHOICES = (
        ('Reader', 'Reader'),
        ('Journalist', 'Journalist'),
        ('Editor', 'Editor'),
    )
    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default='Reader')
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='employees')
    subscribed_journalists = models.ManyToManyField(
        'self',
        symmetrical=False,
        blank=True,
        limit_choices_to={'role': 'Journalist'},
        related_name='subscribers'
    )
    subscribed_publishers = models.ManyToManyField(
        Publisher,
        blank=True,
        related_name='subscribers'
    )

    def __str__(self):
        return self.username


class Article(models.Model):
    """
    Represents a news article created by a journalist.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    editor_approved = models.BooleanField(default=False)
    article_author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    independent_journalist = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Newsletter(models.Model):
    """
    Represents a newsletter created by a journalist.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    editor_approved = models.BooleanField(default=False)
    newsletter_author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    independent_journalist = models.BooleanField(default=False)

    def __str__(self):
        return self.title
