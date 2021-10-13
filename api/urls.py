from django.urls import path

from api import views


urlpatterns = [
    path('auth/login/', views.LoginAuthToken.as_view()),
    path('auth/register/', views.RegisterAccountView.as_view()),
    path('auth/confirm_email/<str:token>', views.ValidateEmailAccountView.as_view(), name="email_verification"),
    path('auth/ask_recovery/', views.PasswordRecoveryAskCode.as_view()),
    path('auth/check_password_code/', views.ValidatePasswordRecoveryCodeView.as_view()),
    path('auth/password_recovery/', views.PasswordRecoveryView.as_view())
]
