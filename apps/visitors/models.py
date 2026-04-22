import secrets
from io import BytesIO

import qrcode
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.urls import reverse
from django.utils import timezone

from apps.common.models import TimeStampedModel


class Visit(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CHECKED_IN = 'CHECKED_IN', 'Checked-in'
        CHECKED_OUT = 'CHECKED_OUT', 'Checked-out'

    reference_no = models.CharField(max_length=30, unique=True, db_index=True)
    visitor_name = models.CharField(max_length=120)
    visitor_phone = models.CharField(max_length=30, db_index=True)
    visitor_email = models.EmailField(blank=True)
    visitor_company = models.CharField(max_length=120, blank=True)
    visitor_id_type = models.CharField(max_length=50, blank=True)
    visitor_id_no = models.CharField(max_length=80, blank=True)
    purpose_of_visit = models.CharField(max_length=255)
    host_name = models.CharField(max_length=120, db_index=True)
    host_department = models.CharField(max_length=120, blank=True)
    host_phone = models.CharField(max_length=30, blank=True)
    host_email = models.EmailField(blank=True)
    visit_date = models.DateField(db_index=True)
    visit_time = models.TimeField()
    qr_token = models.CharField(max_length=96, unique=True, db_index=True)
    qr_code_image = models.ImageField(upload_to='qr_codes/', blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    checked_in_at = models.DateTimeField(blank=True, null=True)
    checked_out_at = models.DateTimeField(blank=True, null=True)
    checked_in_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='checked_in_visits',
        blank=True,
        null=True,
    )
    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='checked_out_visits',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['reference_no']),
            models.Index(fields=['qr_token']),
            models.Index(fields=['status']),
            models.Index(fields=['visit_date']),
            models.Index(fields=['visitor_phone']),
            models.Index(fields=['host_name']),
        ]

    def __str__(self):
        return f'{self.reference_no} - {self.visitor_name}'

    @classmethod
    def generate_reference_no(cls):
        date_part = timezone.localdate().strftime('%Y%m%d')
        for _ in range(10):
            candidate = f'VIS-{date_part}-{secrets.randbelow(900000) + 100000}'
            if not cls.objects.filter(reference_no=candidate).exists():
                return candidate
        raise RuntimeError('Unable to generate a unique visit reference number.')

    @classmethod
    def generate_qr_token(cls):
        for _ in range(10):
            candidate = secrets.token_urlsafe(48)
            if not cls.objects.filter(qr_token=candidate).exists():
                return candidate
        raise RuntimeError('Unable to generate a unique QR token.')

    @property
    def qr_lookup_url(self):
        return f'{settings.SITE_URL}{reverse("reception:scan-token", kwargs={"token": self.qr_token})}'

    def generate_qr_code(self, save=True):
        image = qrcode.make(self.qr_lookup_url)
        buffer = BytesIO()
        image.save(buffer, format='PNG')
        filename = f'{self.reference_no}.png'
        self.qr_code_image.save(filename, ContentFile(buffer.getvalue()), save=save)

    def can_check_in(self):
        return self.status == self.Status.PENDING

    def can_check_out(self):
        return self.status == self.Status.CHECKED_IN

    @transaction.atomic
    def perform_check_in(self, user):
        locked = Visit.objects.select_for_update().get(pk=self.pk)
        if not locked.can_check_in():
            raise ValidationError('Only pending visits can be checked in.')
        locked.status = self.Status.CHECKED_IN
        locked.checked_in_at = timezone.now()
        locked.checked_in_by = user
        locked.save(update_fields=['status', 'checked_in_at', 'checked_in_by', 'updated_at'])
        AuditLog.objects.create(visit=locked, action=AuditLog.Action.CHECK_IN, action_by=user)
        self.refresh_from_db()
        return locked

    @transaction.atomic
    def perform_check_out(self, user):
        locked = Visit.objects.select_for_update().get(pk=self.pk)
        if not locked.can_check_out():
            raise ValidationError('Only checked-in visits can be checked out.')
        locked.status = self.Status.CHECKED_OUT
        locked.checked_out_at = timezone.now()
        locked.checked_out_by = user
        locked.save(update_fields=['status', 'checked_out_at', 'checked_out_by', 'updated_at'])
        AuditLog.objects.create(visit=locked, action=AuditLog.Action.CHECK_OUT, action_by=user)
        self.refresh_from_db()
        return locked

    def clean(self):
        if self.visit_date and self.visit_date < timezone.localdate():
            raise ValidationError({'visit_date': 'Visit date cannot be in the past.'})


class AuditLog(TimeStampedModel):
    class Action(models.TextChoices):
        SUBMITTED = 'SUBMITTED', 'Submitted'
        CHECK_IN = 'CHECK_IN', 'Checked in'
        CHECK_OUT = 'CHECK_OUT', 'Checked out'

    visit = models.ForeignKey(Visit, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=30, choices=Action.choices)
    action_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True)
    note = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.visit.reference_no} - {self.get_action_display()}'
