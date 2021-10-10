from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from chat.models import ChatSession, Chat, ChatHistory
from chat.resolvers import MethodResolver, SerializerResolver, AbstractResolver
from chat.serializers import ContactSerializer


async def run_resolver(resolver, data):
    if isinstance(resolver, AbstractResolver):
        resolver.set_data(data)
        return await resolver.resolve()


class ChatManager:
    def __init__(self, consumer):
        self.consumer = consumer
        self.user = None
        self.room_name = ""
        self.chat_session = None

        self.resolvers = {
            "authorization": MethodResolver(self.authorization),
            "get_contacts": SerializerResolver(
                serializer=ContactSerializer,
                queryset=Chat.objects,
                query_filter={"members__exact": lambda instance, data=None: instance.user.id},
                context=self,
                args={
                    "many": True
                }
            ),
            "message": MethodResolver(self.message_receive, context=self),
            "get_contact": SerializerResolver(
                serializer=ContactSerializer,
                queryset=Chat.objects,
                query_get={"pk": lambda instance, data: data["id"]}
            )
        }

    async def route_resolve(self, content):
        await sync_to_async(print)(content)
        if "type" not in content:
            await self._send_response("type_not_provided", {
                "message": "type route not provided"
            })

        if "data" not in content:
            await self._send_response("data_not_provided", {
                "message": "data not provided"
            })

        if content["type"] not in self.resolvers:
            await self._send_response("type_not_found", {
                "message": "type route not found"
            })

        response = await run_resolver(self.resolvers[content["type"]], content["data"])
        if response is not None:
            await self._send_response(f"{content['type']}_response", response)

    async def authorization(self, data):
        if "token" in data:
            try:
                token = await self.get_token(data["token"])
                user = token.user
                if not user.is_active:
                    return {
                        "status": "error",
                        "message": "Inactive user"
                    }

                self.user = user
                chat_session, created = await self.create_or_get_chat_session(user)

                self.chat_session = chat_session

                await self.set_online(True)

                self.room_name = str(chat_session.id)
                sync_to_async(print)(self.room_name)
                await self.consumer.timeout_stop()
                await self.consumer.set_group()

                return {
                    "status": "success"
                }
            except Token.DoesNotExist:
                return {
                    "status": "error",
                    "message": "Invalid token provided"
                }

    async def message_receive(self, data):
        chat = await self.get_chat(data["to"])
        await self.add_chat_history(data["content"], chat)

    @database_sync_to_async
    def set_online(self, value: bool):
        if self.chat_session:
            self.chat_session.online = value
            self.chat_session.save()

    @database_sync_to_async
    def get_token(self, token):
        return Token.objects.select_related('user').get(key=token)

    @database_sync_to_async
    def get_chat_by_user(self, user_pk):
        chat, created = Chat.objects.filter(members__exact=user_pk).get_or_create(members__exact=self.user.id)
        if created:
            chat.members.add(user_pk, self.user)
            chat.save()
        return chat, created

    @database_sync_to_async
    def add_chat_history(self, content, chat):
        chat_history = ChatHistory.objects.create(content=content, chat=chat, sender=self.user)
        return chat_history

    @database_sync_to_async
    def get_chat(self, chat_id):
        return Chat.objects.get(pk=chat_id)

    @database_sync_to_async
    def create_or_get_chat_session(self, user):
        return ChatSession.objects.get_or_create(user=user)

    async def on_disconnect(self):
        await self.set_online(False)

    async def _send_response(self, response_type: str, data):
        return await self.consumer.send_response(response_type, data)
