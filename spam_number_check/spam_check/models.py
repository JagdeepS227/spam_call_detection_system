from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import PHONE_NUMBER_LENGTH
from .managers import CustomUserManager

# Create your models here.

class User(AbstractUser):
    username = models.CharField(max_length=150, blank=True)
    name = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=PHONE_NUMBER_LENGTH, unique=True, db_index=True)
    email = models.EmailField(blank=True, null=True)
    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.name} ({self.phone_number})"

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.phone_number
        super().save(*args, **kwargs)

class Contact(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contacts'
    )
    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=PHONE_NUMBER_LENGTH, db_index=True)
    class Meta:
        unique_together = ('owner', 'phone_number')
    def __str__(self):
        return f"{self.name} ({self.phone_number})"

class SpamReport(models.Model):
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='spam_reports'
    )
    phone_number = models.CharField(max_length=PHONE_NUMBER_LENGTH, db_index=True)
    reported_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('reporter', 'phone_number')

    def __str__(self):
        return f"{self.phone_number} reported spam by {self.reporter}"

    def save(self, *args, **kwargs):
        created = not self.pk
        super().save(*args, **kwargs)

        if created:
            obj, _ = PhoneNumberMeta.objects.get_or_create(phone_number=self.phone_number)
            obj.spam_count += 1
            obj.save()

class PhoneNumberMeta(models.Model):
    phone_number = models.CharField(max_length=PHONE_NUMBER_LENGTH, unique=True, db_index=True)
    spam_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.phone_number} ({self.spam_count} spam reports)"