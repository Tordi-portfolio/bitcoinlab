from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('balance', views.balance, name='balance'),
    path('manage_balances', views.manage_balances, name='manage_balances'),
    path("withdraw/", views.withdraw, name="withdraw"),
    path('transaction', views.transaction, name='transaction'),
    path('deposit', views.deposit, name='deposit'),
    path('admin/deposits/', views.deposit_submissions_admin, name='deposit_submissions'),
    path('deposit/', views.deposit_form_view, name='deposit'),


    # New Admin Form URL
    path('create_transaction/', views.create_transaction, name='create_transaction'),

    # Auth
    path('register/', views.RegisterView, name='register'),
    path('login/', views.LoginView, name='login'),
    path('logout/', views.LogoutView, name='logout'),
    path('forgot-password/', views.ForgotPassword, name='forgot-password'),
    path('password-reset-sent/<str:reset_id>/', views.PasswordResetSent, name='password-reset-sent'),
    path('reset-password/<str:reset_id>/', views.ResetPassword, name='reset-password'),
]