from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import CustomUser, Article, Newsletter, Publisher


class ApiReaderViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('api_reader_view')

        # Create a Publisher
        self.publisher = Publisher.objects.create(name="Test Publisher")

        # Create Users
        self.reader = CustomUser.objects.create_user(
            username='sue', password='password', role='Reader',
            email='sue@gmail.com'
        )
        self.journalist = CustomUser.objects.create_user(
            username='john', password='password', role='Journalist',
            publisher=self.publisher, email='john@gmail.com'
        )
        self.independent_journalist = CustomUser.objects.create_user(
            username='tom', password='password', role='Editor',
            email='tom@gmail.com'
        )

        # Article from Publisher approved
        self.pub_article = Article.objects.create(
            title="Publisher Article",
            content="Content",
            article_author=self.journalist,
            editor_approved=True
        )

        # Newsletter from Publisher approved
        self.pub_newsletter = Newsletter.objects.create(
            title="Publisher Newsletter",
            content="Content",
            newsletter_author=self.journalist,
            editor_approved=True
        )

        # Article from independent journalist
        self.ind_article = Article.objects.create(
            title="Independent Article",
            content="Content",
            article_author=self.independent_journalist,
            independent_journalist=True
        )

        # Newsletter from independent journalist
        self.ind_newsletter = Newsletter.objects.create(
            title="Independent Newsletter",
            content="Content",
            newsletter_author=self.independent_journalist,
            independent_journalist=True
        )

        # Unapproved article should not appear
        self.unapproved_article = Article.objects.create(
            title="Unapproved Article",
            content="Content",
            article_author=self.journalist,
            editor_approved=False
        )

    def test_api_reader_view_success(self):
        """
        Test that a subscribed reader receives the correct content.
        """
        # Subscribe the reader
        self.reader.subscribed_publishers.add(self.publisher)
        self.reader.subscribed_journalists.add(self.independent_journalist)

        # Authenticate
        self.client.force_authenticate(user=self.reader)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # Verify Publisher Articles
        self.assertEqual(len(data['publishers_articles']), 1)
        self.assertEqual(
            data['publishers_articles'][0]['id'], self.pub_article.id)

        # Verify Publisher Newsletters
        self.assertEqual(len(data['publishers_newsletters']), 1)
        self.assertEqual(
            data['publishers_newsletters'][0]['id'], self.pub_newsletter.id)

        # Verify Independent Articles
        self.assertEqual(len(data['journalists_articles']), 1)
        self.assertEqual(
            data['journalists_articles'][0]['id'], self.ind_article.id)

        # Verify Independent Newsletters
        self.assertEqual(len(data['journalists_newsletters']), 1)
        self.assertEqual(
            data['journalists_newsletters'][0]['id'], self.ind_newsletter.id)

    def test_api_reader_view_wrong_role(self):
        """
        Test that non-Reader roles are forbidden.
        """
        self.client.force_authenticate(user=self.journalist)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(
            response.data['error'], 'This view is for Readers only.')
