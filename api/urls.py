from django.urls import path

from api import views

urlpatterns = [
    path('login/', views.LoginAuthToken.as_view()),
]
