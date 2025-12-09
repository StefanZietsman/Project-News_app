from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import PasswordChangeForm, AuthenticationForm
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth import models as auth_models
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from .forms import RegisterForm, ArticleForm, NewsletterForm
from .models import Article, Publisher, Newsletter, CustomUser
from .functions.tweet import Tweet
from .serializers import ArticleSerializer, NewsletterSerializer
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.decorators import permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


def article_list(request):
    """
    Displays a list of all articles and newsletters.
    """
    articles = Article.objects.all().order_by('title')
    newsletters = Newsletter.objects.all().order_by('title')
    context = {
        'article_list': articles,
        'newsletter_list': newsletters
    }
    return render(request, 'news_app/article_list.html', context)


def register_user(request):
    """
    Handles user registration, including role and publisher assignment.
    """
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            role = form.cleaned_data.get('role')
            publisher_name = form.cleaned_data.get('publisher')

            # Ensure users with specific roles are associated with a
            # publisher
            if role in ['Editor', 'Journalist'] and not publisher_name:
                messages.error(
                    request, 'Editors and Journalists must select a publisher.'
                )
                # Re-render the form with the error
                return render(
                    request, 'news_app/register.html', {'form': form})

            user = form.save(commit=False)

            # Only add Publisher for editor and journalist
            if role in ['Editor', 'Journalist']:
                if publisher_name:
                    publisher, created = Publisher.objects.get_or_create(
                        name=publisher_name)
                    user.publisher = publisher

            # Readers should not be associated with a publisher
            if role == 'Reader':
                user.publisher = None  # Ensure reader has no publisher
            user.save()

            # Add user to a group with the same name as their role
            group, created = (
                auth_models.Group.objects.get_or_create(name=user.role))
            group.user_set.add(user)
            messages.success(
                request, 'Registration successful. You can now log in.')
            return redirect('article_list')
    else:
        form = RegisterForm()

    context = {'form': form}
    return render(request, 'news_app/register.html', context)


def login_user(request):
    """
    Handles user login.
    """
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.info(request, f"Welcome back, {user.username}.")
            return redirect('article_list')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()
    return render(request, 'news_app/login.html', {'form': form})


def logout_user(request):
    """
    Handles user logout.
    """
    logout(request)
    return render(request, 'news_app/logout.html')


@login_required
def change_password_user(request):
    """
    Allows a logged-in user to change their password.
    """
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(
                request, 'Your password was successfully updated!')
            return redirect('article_list')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)

    context = {'form': form}
    return render(request, 'news_app/change_password.html', context)


@login_required
@permission_required('news_app.add_article', raise_exception=True)
def add_article(request):
    """
    Allows a journalist to add a new article.
    """
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            # Set the author of the article to the currently logged-in
            # user
            article.article_author = request.user

            # Check if user has a publisher and handle article's
            # publisher
            if request.user.publisher:
                publish_as = request.POST.get('publish_as')
                if publish_as == 'publisher':
                    # Associate article with the author's publisher
                    article.publisher = request.user.publisher
                else:
                    article.publisher = None
                    article.independent_journalist = True

                    # Email subscribers of the independent journalist
                    journalist = request.user
                    subscribers = (
                        CustomUser.objects.filter(
                            subscribed_journalists=journalist))
                    if subscribers.exists():
                        subject = (
                            f'New Article from {journalist.username}: '
                            f'{article.title}')
                        message = render_to_string(
                            'news_app/independent_article_email.html',
                            {
                             'article': article,
                             'journalist': journalist,
                            })
                        # Get email addresses of all subscribers
                        recipient_list = [
                            subscriber.email for subscriber in subscribers
                            if subscriber.email]
                        if recipient_list:
                            email = EmailMessage(
                                subject, message, to=recipient_list)
                            email.send()

                    # Tweet about the new article
                    try:
                        tweet_handler = Tweet()
                        tweet_text = (
                            f'New Article from {journalist.username}: '
                            f'{article.title}\n{article.content}')
                        tweet_handler.make_tweet({"text": tweet_text})
                        messages.info(
                            request, "A tweet has been posted for the new "
                            "article.")
                    except Exception as e:
                        # Log the error and inform the user
                        print(f"Error posting tweet: {e}")
                        messages.warning(
                            request, f"Article approved, but failed to post a "
                            f"tweet. Error: {e}")

            article.save()
            form.save_m2m()  # Needed for ManyToMany fields like categories
            messages.success(request, 'Article added successfully.')
            return redirect('article_list')
    else:
        form = ArticleForm()
    return render(request, 'news_app/add_article.html', {'form': form})


def view_article(request, pk):
    """
    Displays a single article.
    """
    article = get_object_or_404(Article, pk=pk)
    context = {
        'article': article
    }
    return render(request, 'news_app/view_article.html', context)


@login_required
@permission_required('news_app.change_article', raise_exception=True)
def edit_article(request, pk):
    """
    Allows an editor or journalist to edit an article. Editors can
    approve articles.
    """
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            article_instance = form.save(commit=False)

            # Store the approval status before any changes
            was_approved = article.editor_approved

            # Handle editor approval
            if request.user.role == 'Editor':
                is_approved = request.POST.get('editor_approved') == 'on'
                article_instance.editor_approved = is_approved

                # If article is approved now and wasn't before, send
                # notifications
                if is_approved and not was_approved:
                    publisher = article_instance.article_author.publisher
                    if publisher:
                        subscribers = publisher.subscribers.all()
                        if subscribers:
                            subject = (
                                f"New Article Published: "
                                f"{article_instance.title}")
                            # Render email content from a template for
                            # better practice
                            message = render_to_string(
                                'news_app/article_email.html',
                                {
                                 'article': article_instance,
                                 'publisher': publisher,
                                })
                            # Get email addresses of all publisher
                            # subscribers
                            recipient_list = [
                                subscriber.email for subscriber in subscribers
                                if subscriber.email]
                            email = EmailMessage(
                                subject, message, to=recipient_list)
                            email.send()

                    # Tweet about the new article
                    try:
                        tweet_handler = Tweet()
                        tweet_text = (
                            f'New article from {publisher.name}: '
                            f'{article_instance.title}\n'
                            f'{article_instance.content}')
                        tweet_handler.make_tweet({"text": tweet_text})
                        messages.info(
                            request, "A tweet has been posted for the new "
                            "article.")
                    except Exception as e:
                        # Log the error and inform the user
                        print(f"Error posting tweet: {e}")
                        messages.warning(
                            request, f"Article approved, but failed to post a "
                            f"tweet. Error: {e}")

            article_instance.save()
            messages.success(request, 'Article updated successfully.')
            return redirect('article_list')
    else:
        form = ArticleForm(instance=article)

    context = {'form': form, 'article': article}
    return render(request, 'news_app/edit_article.html', context)


@login_required
@permission_required('news_app.delete_article', raise_exception=True)
def delete_article(request, pk):
    """
    Allows an journalist to delete their article.
    """
    article = get_object_or_404(Article, pk=pk)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Article deleted successfully.')
        return redirect('article_list')

    return render(
        request, 'news_app/delete_article.html', {'article': article})


@login_required
@permission_required('news_app.add_newsletter', raise_exception=True)
def add_newsletter(request):
    """
    Allows a journalist to add a new newsletter.
    """
    if request.method == 'POST':
        form = NewsletterForm(request.POST, request.FILES)
        if form.is_valid():
            newsletter = form.save(commit=False)
            # Set the author of the newsletter to the currently
            # logged-in user
            newsletter.newsletter_author = request.user

            # Check if user has a publisher and handle newsletter
            # publisher
            if request.user.publisher:
                publish_as = request.POST.get('publish_as')
                if publish_as == 'publisher':
                    # Associate newsletter with the author's publisher
                    newsletter.publisher = request.user.publisher
                else:
                    newsletter.publisher = None
                    newsletter.independent_journalist = True

                    # Email subscribers of the independent journalist
                    journalist = request.user
                    subscribers = (
                        CustomUser.objects.filter(
                            subscribed_journalists=journalist))
                    if subscribers.exists():
                        subject = (
                            f"New Newsletter from {journalist.username}: "
                            f"{newsletter.title}")
                        message = render_to_string(
                            'news_app/independent_newsletter_email.html',
                            {
                             'newsletter': newsletter,
                             'journalist': journalist,
                            })
                        # Get email addresses of all subscribers
                        recipient_list = [
                            subscriber.email for subscriber in subscribers
                            if subscriber.email]
                        if recipient_list:
                            email = EmailMessage(
                                subject, message, to=recipient_list)
                            email.send()

                    # Tweet about the new newsletter
                    try:
                        tweet_handler = Tweet()
                        tweet_text = (
                            f'New Newsletter from {journalist.username}: '
                            f'{newsletter.title}\n{newsletter.content}')
                        tweet_handler.make_tweet({"text": tweet_text})
                        messages.info(
                            request, "A tweet has been posted for the new "
                            "newsletter.")
                    except Exception as e:
                        # Log the error and inform the user
                        print(f"Error posting tweet: {e}")
                        messages.warning(
                            request, f"Newsletter approved, but failed to post"
                            f" a tweet. Error: {e}")

            newsletter.save()
            form.save_m2m()  # Needed for ManyToMany fields like categories
            messages.success(request, 'Newsletter added successfully.')
            return redirect('article_list')
    else:
        form = NewsletterForm()
    return render(request, 'news_app/add_newsletter.html', {'form': form})


def view_newsletter(request, pk):
    """
    Displays a single newsletter.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    context = {
        'newsletter': newsletter
    }
    return render(request, 'news_app/view_newsletter.html', context)


@login_required
@permission_required('news_app.change_newsletter', raise_exception=True)
def edit_newsletter(request, pk):
    """
    Allows an editor or journalist to edit a newsletter. Editors can
    approve newsletters.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.method == 'POST':
        form = NewsletterForm(request.POST, request.FILES, instance=newsletter)
        if form.is_valid():
            newsletter_instance = form.save(commit=False)

            # Store the approval status before any changes
            was_approved = newsletter.editor_approved

            # Handle editor approval
            if request.user.role == 'Editor':
                is_approved = request.POST.get('editor_approved') == 'on'
                newsletter_instance.editor_approved = is_approved

                # If article is approved now and wasn't before, send
                # notifications
                if is_approved and not was_approved:
                    publisher = newsletter_instance.newsletter_author.publisher
                    if publisher:
                        subscribers = publisher.subscribers.all()
                        if subscribers:
                            subject = (
                                f"New Newsletter Published: "
                                f"{newsletter_instance.title}")
                            # Render email content from a template for
                            # better practice
                            message = render_to_string(
                                'news_app/newsletter_email.html',
                                {
                                 'newsletter': newsletter_instance,
                                 'publisher': publisher,
                                })
                            # Get email addresses of all publisher
                            # subscribers
                            recipient_list = [
                                subscriber.email for subscriber in subscribers
                                if subscriber.email]
                            email = EmailMessage(
                                subject, message, to=recipient_list)
                            email.send()

                    # Tweet about the new newsletter
                    try:
                        tweet_handler = Tweet()
                        tweet_text = (
                            f'New Newsletter from {publisher.name}: '
                            f'{newsletter_instance.title}\n'
                            f'{newsletter_instance.content}')
                        tweet_handler.make_tweet({"text": tweet_text})
                        messages.info(
                            request, "A tweet has been posted for the new "
                            "newsletter.")
                    except Exception as e:
                        # Log the error and inform the user
                        print(f"Error posting tweet: {e}")
                        messages.warning(
                            request, f"Newsletter approved, but failed to post"
                            f" a tweet. Error: {e}")

            newsletter_instance.save()
            messages.success(request, 'Newsletter updated successfully.')
            return redirect('article_list')
    else:
        form = NewsletterForm(instance=newsletter)

    context = {'form': form, 'newsletter': newsletter}
    return render(request, 'news_app/edit_newsletter.html', context)


@login_required
@permission_required('news_app.delete_newsletter', raise_exception=True)
def delete_newsletter(request, pk):
    """
    Allows an journalist to delete their newsletter.
    """
    newsletter = get_object_or_404(Newsletter, pk=pk)
    if request.method == 'POST':
        newsletter.delete()
        messages.success(request, 'Newsletter deleted successfully.')
        return redirect('article_list')

    return render(
        request, 'news_app/delete_newsletter.html', {'newsletter': newsletter})


@login_required
def manage_subscriptions(request):
    """
    Allows a reader to subscribe/unsubscribe from journalists and
    publishers.
    """
    # Ensure only 'Reader' role can access this page
    if request.user.role != 'Reader':
        messages.error(request, "Only readers can manage subscriptions.")
        return redirect('article_list')

    if request.method == 'POST':
        # Get lists of IDs from the form submission
        subscribed_journalists_ids = request.POST.getlist('journalists')
        subscribed_publishers_ids = request.POST.getlist('publishers')

        # Update user's subscriptions
        request.user.subscribed_journalists.set(subscribed_journalists_ids)
        request.user.subscribed_publishers.set(subscribed_publishers_ids)

        messages.success(request, "Your subscriptions have been updated.")
        return redirect('article_list')

    # GET request: display the subscription options
    journalists = CustomUser.objects.filter(role='Journalist')
    publishers = Publisher.objects.all()

    context = {'journalists': journalists, 'publishers': publishers}
    return render(request, 'news_app/manage_subscriptions.html', context)


def password_reset_request(request):
    """
    Handles the request for a password reset link.
    """
    if request.method == 'POST':
        email = request.POST.get('email')
        associated_users = CustomUser.objects.filter(email=email)
        # If user(s) with the email exist, send reset link
        if associated_users.exists():
            for user in associated_users:
                current_site = get_current_site(request)
                mail_subject = 'Reset your password'
                # The message is rendered from a template
                message = render_to_string(
                    'news_app/password_reset_email.html',
                    {
                     'user': user,
                     'domain': current_site.domain,
                     'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                     'token': default_token_generator.make_token(user),
                    })
                email_message = EmailMessage(
                    mail_subject, message, to=[user.email]
                )
                email_message.send()
            messages.success(
                request, 'A password reset link has been sent to your email '
                'address if it exists in our system.')
            return redirect('article_list')
        else:
            # We show the same message to avoid leaking user information
            messages.success(
                request, 'A password reset link has been sent to your email '
                'address if it exists in our system.')
            return redirect('article_list')

    return render(request, 'news_app/password_reset_form.html')


def password_reset_confirm(request, uidb64=None, token=None):
    """
    Handles the password reset confirmation after a user clicks the
    link.
    """
    # Decode the user ID and find the user
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        # If the link is valid, show the password set form
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request, 'Your password has been set. You may go ahead and'
                    ' log in now.')
                return redirect('article_list')
        else:
            form = SetPasswordForm(user)
        return render(
            request, 'news_app/password_reset_confirm.html', {'form': form})
    else:
        # If the link is invalid, show an error
        messages.error(
            request, 'The reset link was invalid, possibly because it has'
            ' already been used. Please request a new password reset.')
        return redirect('password_reset_request')


@api_view(['GET'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([IsAuthenticated])
def api_reader_view(request):
    """
    API endpoint for a 'Reader' to get articles and
    newsletters they are subscribed to.
    """
    user = request.user
    if user.role != 'Reader':
        return Response(
            {'error': 'This view is for Readers only.'}, status=403)

    # Get subscribed publishers and journalists
    subscribed_publishers = user.subscribed_publishers.all()
    subscribed_journalists = user.subscribed_journalists.all()

    # Get approved articles from subscribed publishers
    publisher_articles = Article.objects.filter(
        article_author__publisher__in=subscribed_publishers,
        editor_approved=True
    ).select_related('article_author')

    # Get approved newsletters from subscribed publishers
    publisher_newsletters = Newsletter.objects.filter(
        newsletter_author__publisher__in=subscribed_publishers,
        editor_approved=True
    ).select_related('newsletter_author')

    # Get content from subscribed independent journalists
    independent_articles = Article.objects.filter(
        article_author__in=subscribed_journalists,
        independent_journalist=True
    ).select_related('article_author')

    # Get newsletters from independent journalists
    independent_newsletters = Newsletter.objects.filter(
        newsletter_author__in=subscribed_journalists,
        independent_journalist=True
    ).select_related('newsletter_author')

    # Serialize the data
    publisher_articles_data = (
        ArticleSerializer(publisher_articles, many=True).data)
    publisher_newsletters_data = (
        NewsletterSerializer(publisher_newsletters, many=True).data)
    independent_articles_data = (
        ArticleSerializer(independent_articles, many=True).data)
    independent_newsletters_data = (
        NewsletterSerializer(independent_newsletters, many=True).data)

    # Combine independent content
    subscribed_content = {
        'publishers_articles': publisher_articles_data,
        'publishers_newsletters': publisher_newsletters_data,
        'journalists_articles': independent_articles_data,
        'journalists_newsletters': independent_newsletters_data,
    }

    return Response(subscribed_content)
