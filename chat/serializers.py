from django.contrib.auth.models import User
from rest_framework import serializers

from chat.models import Chat, ChatSession


class ContactSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    online = serializers.SerializerMethodField()

    def get_name(self, instance: Chat):
        user = instance.members.exclude(id=self.context.user.pk).first()
        return '{} {}'.format(user.first_name, user.last_name)

    def get_online(self, instance: Chat):
        user = instance.members.exclude(id=self.context.user.pk).first()
        try:
            chat_session = ChatSession.objects.get(user=user.pk)
            return chat_session.online
        except ChatSession.DoesNotExist:
            return False

    class Meta:
        model = Chat
        fields = ('pk', 'name', 'online')
