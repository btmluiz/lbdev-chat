from rest_framework import serializers

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


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


class LoginSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

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
