from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import Article, Newsletter
from .models import CustomUser


class RegisterForm(UserCreationForm):
    """
    A custom user registration form that includes a field for selecting
    a user role.
    """
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES, required=True,
        help_text="Select a user role.")
    publisher = forms.CharField(
        max_length=100, required=True,
        help_text="If you are a Reader role, please enter 'Reader'.")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('email', 'role')


class ArticleForm(forms.ModelForm):
    """
    A form for creating and updating Article instances.
    """
    class Meta:
        model = Article
        fields = ['title', 'content']


class NewsletterForm(forms.ModelForm):
    """
    A form for creating and updating Newsletter instances.
    """
    class Meta:
        model = Newsletter
        fields = ['title', 'content']
