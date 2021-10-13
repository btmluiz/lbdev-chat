from django.urls import path

from chat import views

urlpatterns = [
    path('test_email/', views.test_email)
]
