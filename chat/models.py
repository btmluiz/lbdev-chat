import uuid

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import models

from api.models import User, Model
# Create your models here.


class ChatSession(Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    online = models.BooleanField(default=False)


class Chat(Model):
    created_at = models.DateTimeField(auto_now_add=True)
    chat_key = models.UUIDField(default=uuid.uuid4, unique=True)
    members = models.ManyToManyField(to=User)


class ChatHistory(Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    received_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        sessions = ChatSession.objects.filter(user__chat=self.chat).all()
        for chat_session in sessions:
            print(str(chat_session.id))
            if self.sender == chat_session.user:
                direction = "send"
            else:
                direction = "received"
            data = {
                "pk": str(self.chat.pk),
                "data": {
                    "direction": direction,
                    "content": self.content,
                    "time": self.created_at.isoformat()
                }
            }

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                str(chat_session.id),
                {
                    "type": "send_message",
                    "data": {"type": "message", "data": data}
                }
            )
