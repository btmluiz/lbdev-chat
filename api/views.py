from django.contrib.auth import login
from django.utils.translation import gettext_lazy as _

# Create your views here.
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView, CreateAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from api import serializers, status_messages
from api.models import User, ConfirmToken
from api.serializers import UserSerializer, LoginResponseSerializer, RegisterAccountSerializer, \
    ConfirmAccountSerializer, ResponseSerializer, ValidatePasswordRecoveryCodeSerializer, \
    AskPasswordRecoveryCodeSerializer, PasswordRecoverySerializer
from api.utils import email_hide


class LoginAuthToken(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.LoginSerializer

    @swagger_auto_schema(responses={200: LoginResponseSerializer()}, tags=['auth'])
    def post(self, request):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            response_serializer = LoginResponseSerializer(data={
                'token': token.key,
                'data': UserSerializer(instance=user).data
            })
            response_serializer.is_valid()

            login(request, user)

            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


class RegisterAccountView(CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterAccountSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_serializer = ResponseSerializer(data={
            "status": status_messages.SUCCESS,
            "message": _("A verification email was send to %s") % (email_hide(serializer.instance.email))
        })
        response_serializer.is_valid()
        headers = self.get_success_headers(response_serializer.data)

        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @swagger_auto_schema(tags=['auth'], responses={201: ResponseSerializer()})
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class ValidateEmailAccountView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ConfirmAccountSerializer

    @swagger_auto_schema(responses={200: ResponseSerializer()}, tags=['auth'])
    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            chat_confirm = serializer.instance
            chat_confirm.validated = True
            chat_confirm.user.email_validated = True
            chat_confirm.user.save()
            chat_confirm.save()

            response_serializer = ResponseSerializer(data={
                "status": status_messages.SUCCESS,
                "message": _("Validation successfully")
            })
            response_serializer.is_valid()
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            response_serializer = ResponseSerializer(data={
                "status": status_messages.FAILED,
                "message": _("Token expired")
            })
            response_serializer.is_valid()
            return Response(response_serializer.data, status=status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryAskCode(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = AskPasswordRecoveryCodeSerializer

    @swagger_auto_schema(tags=['auth'], responses={201: ResponseSerializer()})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            password_code = serializer.instance
            password_code.send_password_recovery()

            response_serializer = ResponseSerializer(data={
                "status": status_messages.SUCCESS,
                "message": _("Password code send")
            })
            response_serializer.is_valid()

            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        else:
            response_serializer = ResponseSerializer(data={
                "status": status_messages.FAILED,
                "message": serializer.errors
            })
            response_serializer.is_valid()
            return Response(response_serializer.data, status=status.HTTP_400_BAD_REQUEST)


class ValidatePasswordRecoveryCodeView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ValidatePasswordRecoveryCodeSerializer

    @swagger_auto_schema(tags=['auth'], responses={200: ResponseSerializer()})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            response_serializer = ResponseSerializer(data={
                "status": status_messages.SUCCESS,
                "message": _("Code still valid")
            })
            response_serializer.is_valid()

            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            response_serializer = ResponseSerializer(data={
                "status": status_messages.FAILED,
                "message": serializer.errors
            })
            response_serializer.is_valid()
            return Response(response_serializer.data, status=status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryView(GenericAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = PasswordRecoverySerializer

    @swagger_auto_schema(tags=['auth'], responses={200: ResponseSerializer()})
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            response_serializer = ResponseSerializer(data={
                "status": status_messages.SUCCESS,
                "message": _("Password changed successfully")
            })
            response_serializer.is_valid()

            return Response(response_serializer.data, status=status.HTTP_200_OK)
        else:
            response_serializer = ResponseSerializer(data={
                "status": status_messages.FAILED,
                "message": serializer.errors
            })
            response_serializer.is_valid()
            return Response(response_serializer.data, status=status.HTTP_400_BAD_REQUEST)
