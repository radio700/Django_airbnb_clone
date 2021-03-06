import uuid
from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

# Create your models here.


class User(AbstractUser):
    """
    custom user model
    """

    GENDER_MALE = "male"
    GENDER_FEMALE = "female"

    GENDER_CHOICES = (
        (GENDER_MALE, _("male")),
        (GENDER_FEMALE, _("female")),
    )

    LANGUAGE_ENGLISH = "En"
    LANGUAGE_KOREAN = "Ko"

    LANGUAGE_CHOICES = (
        (LANGUAGE_ENGLISH, _("English")),
        (LANGUAGE_KOREAN, _("Korean")),
    )

    CURRENCY_USD = "usd"
    CURRENCY_KRW = "krw"

    CURRENCY_CHOICES = (
        (CURRENCY_USD, "usd"),
        (CURRENCY_KRW, "krw"),
    )

    LOGIN_EMAIL = "email"
    LOGIN_GITHUB = "github"
    LOGING_KAKAO = "kakao"

    LOGIN_CHOICES = (
        (LOGIN_EMAIL, "Email"),
        (LOGIN_GITHUB, "Github"),
        (LOGING_KAKAO, "Kakao"),
    )

    avatar = models.ImageField(upload_to="avatars", blank=True)
    gender = models.CharField(_('gender'), choices=GENDER_CHOICES, max_length=10, blank=True)
    bio = models.TextField(_('bio'),blank=True)
    birthday = models.DateField(_('birthday'),blank=True, null=True)
    language = models.CharField(
        _("language"), choices=LANGUAGE_CHOICES, blank=True, max_length=2, default=LANGUAGE_KOREAN
    )
    currency = models.CharField(
        choices=CURRENCY_CHOICES, blank=True, max_length=3, default=CURRENCY_KRW
    )
    is_superhost = models.BooleanField(default=False)
    login_method = models.CharField(
        max_length=50, choices=LOGIN_CHOICES, default=LOGIN_EMAIL
    )
    email_verified = models.BooleanField(default=False)
    email_secret = models.CharField(max_length=120, default="", blank=True)

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={"pk": self.pk})

    def verify_email(self):
        if self.email_verified is False:
            secret = uuid.uuid4().hex[:20]
            self.email_secret = secret
            html_message = render_to_string("emails/verify_email.html", {"secret": secret})
            send_mail(
                _("Verify Airbnb Account"),
                strip_tags(html_message),
                settings.EMAIL_FROM,
                [self.email],
                fail_silently=False,
                html_message=html_message,
            )
            self.save()
        return
