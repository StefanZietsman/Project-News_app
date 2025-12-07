from django.urls import path
from . import views

urlpatterns = [
    # Article URLs
    path('', views.article_list, name='article_list'),
    path('article/<int:pk>/', views.view_article, name='view_article'),
    path('article/add/', views.add_article, name='add_article'),
    path('article/<int:pk>/edit/', views.edit_article, name='edit_article'),
    path('article/<int:pk>/delete/', views.delete_article,
         name='delete_article'),

    # Authentication URLs
    path('register/', views.register_user, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('change_password/', views.change_password_user,
         name='change_password'),

    # Newsletter URLs
    path('newsletter/<int:pk>/', views.view_newsletter,
         name='view_newsletter'),
    path('newsletter/add/', views.add_newsletter, name='add_newsletter'),
    path('newsletter/<int:pk>/edit/', views.edit_newsletter,
         name='edit_newsletter'),
    path('newsletter/<int:pk>/delete/', views.delete_newsletter,
         name='delete_newsletter'),

    # Subscription URLs
    path('subscriptions/', views.manage_subscriptions,
         name='manage_subscriptions'),

    # Password Reset URLs
    path('password_reset/', views.password_reset_request,
         name='password_reset_request'),
    path('reset/<uidb64>/<token>/', views.password_reset_confirm,
         name='password_reset_confirm'),

    # API URLs
    path('api/reader_view/', views.api_reader_view, name='api_reader_view'),
]
