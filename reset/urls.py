from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    # Other URLs...

    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='auth/password_reset.html'), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(template_name='auth/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='auth/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset_done/', auth_views.PasswordResetCompleteView.as_view(template_name='auth/password_reset_complete.html'), name='password_reset_complete'),

    path('profile/settings/', views.profile_settings, name='profile_settings'),
    path('settings/', views.settings, name='settings'),
    path('profile/password/', views.change_password, name='change_password'),
    path('profile/upload-picture/', views.upload_profile_picture, name='upload_profile_picture'),
]
