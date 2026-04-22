from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.models import TimeStampedModel


class User(AbstractUser, TimeStampedModel):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        RECEPTIONIST = 'RECEPTIONIST', 'Receptionist'

    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=150)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.RECEPTIONIST)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_receptionist(self):
        return self.role == self.Role.RECEPTIONIST or self.is_admin

    def __str__(self):
        return self.full_name or self.username
