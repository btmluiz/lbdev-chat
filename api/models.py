import secrets
import uuid

# db
from random import randint

from django.db import models
# auth
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
# mail
from django.core.mail import send_mail
# utils
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Create your models here.
from lbdev_chat import settings
from lbdev_chat.settings import SITE_NAME, COMPANY_NAME, COMPANY_URL


class Model(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class UserManager(BaseUserManager):

    def _create_user(self, username, email, password, is_staff, is_superuser, **extra_fields):
        now = timezone.now()
        if not username:
            raise ValueError(_('The given username must be set'))
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=True, is_superuser=is_superuser,
                          last_login=now, date_joined=now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        return self._create_user(username, email, password, False, False, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        user = self._create_user(username, email, password, True, True, **extra_fields)
        user.is_active = True
        user.save(using=self._db)
        return user


class User(Model, AbstractBaseUser, PermissionsMixin):
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True, unique=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    email_validated = models.BooleanField(default=False, blank=True)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super(User, self).clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    @property
    def full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        :return:
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    @property
    def short_name(self):
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        return send_mail(subject, message, from_email, [self.email], **kwargs)

    def send_validation_email(self):
        confirm_token = ConfirmToken.objects.create(user=self)

        verification_template = get_template('email/verification.html')

        content = verification_template.render({
            'site_name': SITE_NAME,
            'url': settings.EMAIL_VALIDATION_URL % confirm_token.token,
            'user': self,
            'company_name': COMPANY_NAME,
            'company_url': COMPANY_URL,
        })

        return self.email_user(_("%s - Email validation") % SITE_NAME, confirm_token.token, html_message=content)


class ConfirmToken(Model):
    token = models.CharField(_("Token"), max_length=80, unique=True)
    user = models.ForeignKey(
        User,
        related_name="confirm_token",
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    validated = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.token:
            self.token = self.generate_token()
        return super(ConfirmToken, self).save(*args, **kwargs)

    @classmethod
    def generate_token(cls):
        token = secrets.token_urlsafe(60)
        return token


class PasswordRecoveryCode(Model):
    code_length = 6
    code = models.CharField(_("Code"), max_length=code_length, unique=True)
    user = models.ForeignKey(
        User,
        related_name="password_recovery_code",
        on_delete=models.CASCADE
    )
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        return super(PasswordRecoveryCode, self).save(*args, **kwargs)

    @classmethod
    def generate_code(cls):
        return ''.join(["{}".format(randint(0, 9)) for n in range(0, cls.code_length)])

    def send_password_recovery(self):
        recovery_template = get_template('email/password_recovery.html')

        content = recovery_template.render({
            'site_name': SITE_NAME,
            'code': self.code,
            'user': self.user,
            'company_name': COMPANY_NAME,
            'company_url': COMPANY_URL,
        })

        return self.user.email_user(_("%s - Password recovery") % SITE_NAME, self.code, html_message=content)

