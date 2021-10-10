from django.urls import path, re_path

from chat import consumers

urlpatterns = [
    path('chat', consumers.ChatConsumer.as_asgi())
]
