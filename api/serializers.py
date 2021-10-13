import datetime

from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from rest_framework.validators import UniqueValidator

from api.models import User, ConfirmToken, PasswordRecoveryCode


class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super(DynamicFieldsModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class ValidationSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class LoginSerializer(ValidationSerializer):
    username = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(
        label=_('Password'),
        style={'input_type': 'password'},
        trim_whitespace=False,
        max_length=255,
        write_only=True
    )

    def authenticate(self, **kwargs):
        return authenticate(self.context.get('request'), **kwargs)

    def _validate_user(self, username, password):
        msg = {}
        if not username:
            msg["username"] = _('required')

        if not password:
            msg["password"] = _('required')

        if len(msg) > 0:
            raise serializers.ValidationError([msg])

        user = self.authenticate(username=username, password=password)

        return user

    def validate(self, data):
        username = data.get('username', None)
        password = data.get('password', None)

        user = self._validate_user(username, password)
        if not user:
            raise serializers.ValidationError(
                _('User not found'),
                code='authorization'
            )
        data['user'] = user
        return data


class RegisterAccountSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[UniqueValidator(queryset=User.objects.all())])
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name',)
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("Password fields didn't match")})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        user.send_validation_email()

        return user


class ConfirmAccountSerializer(ValidationSerializer):
    token = serializers.CharField()

    def validate(self, attrs):
        try:
            confirm_token = ConfirmToken.objects.get(token=attrs['token'], validated=False)

            if not (timezone.now() - confirm_token.created) < datetime.timedelta(hours=3):
                raise serializers.ValidationError({"token": "Expired token"})

            self.instance = confirm_token
            return attrs
        except ConfirmToken.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token for email confirmation"})


class AskPasswordRecoveryCodeSerializer(ValidationSerializer):
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        try:
            user = User.objects.get(email=attrs['email'])
            password_code = PasswordRecoveryCode.objects.create(user=user)

            self.instance = password_code

            return attrs
        except User.DoesNotExist:
            raise serializers.ValidationError({'email': _('email not assign to a user')})


class ValidatePasswordRecoveryCodeSerializer(ValidationSerializer):
    code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        try:
            password_code = PasswordRecoveryCode.objects.get(code=attrs['code'])

            if not (timezone.now() - password_code.created) < datetime.timedelta(hours=3):
                password_code.delete()
                raise serializers.ValidationError({"code": "Code expired"})

            self.instance = password_code
            return attrs
        except PasswordRecoveryCode.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token"})


class PasswordRecoverySerializer(ValidationSerializer):
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    def validate(self, attrs):
        try:
            password_code = PasswordRecoveryCode.objects.get(code=attrs['code'])

            if not (timezone.now() - password_code.created) < datetime.timedelta(hours=3):
                password_code.delete()
                raise serializers.ValidationError({"code": "Code expired"})

            password_code.delete()
            self.instance = password_code.user
            self.instance.set_password(attrs['password'])
            self.instance.save()
            return attrs
        except PasswordRecoveryCode.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token"})


class UserSerializer(DynamicFieldsModelSerializer):
    permissions = serializers.SerializerMethodField('list_permissions')

    @staticmethod
    def list_permissions(user):
        permissions = {}
        for permission in user.get_all_permissions():
            _split_perm = permission.split('.')[1]
            _split = _split_perm.split('_')
            if _split[1] not in permissions:
                permissions[_split[1]] = [_split[0]]
            else:
                permissions[_split[1]].append(_split[0])
        return permissions

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name',
                  'is_active', 'is_staff', 'is_superuser', 'permissions')


class LoginResponseSerializer(ValidationSerializer):
    token = serializers.CharField()
    data = UserSerializer()


class ResponseSerializer(ValidationSerializer):
    status = serializers.SlugField()
    message = serializers.CharField()
