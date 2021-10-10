from django.urls import path
from channels.routing import URLRouter

import chat.routing

urlpatterns = [
    path('', URLRouter(chat.routing.urlpatterns))
]
