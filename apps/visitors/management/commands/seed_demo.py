from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.visitors.models import Visit
from apps.visitors.services import create_visit


class Command(BaseCommand):
    help = 'Create demo receptionist and visitor records.'

    def handle(self, *args, **options):
        user_model = get_user_model()
        user, created = user_model.objects.get_or_create(
            username='reception',
            defaults={
                'email': 'reception@example.com',
                'full_name': 'Reception User',
                'role': 'RECEPTIONIST',
                'is_staff': True,
            },
        )
        if created:
            user.set_password('pass12345')
            user.save()

        if not user_model.objects.filter(username='admin').exists():
            user_model.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin12345',
                full_name='Admin User',
                role='ADMIN',
            )

        if not Visit.objects.filter(visitor_phone='+8801711111111').exists():
            create_visit({
                'visitor_name': 'Jane Visitor',
                'visitor_phone': '+8801711111111',
                'visitor_email': 'jane@example.com',
                'visitor_company': 'Acme Ltd',
                'visitor_id_type': 'Passport',
                'visitor_id_no': 'P1234567',
                'purpose_of_visit': 'Project meeting',
                'visit_date': timezone.localdate() + timedelta(days=1),
                'visit_time': '10:30',
                'host_name': 'Sam Host',
                'host_department': 'Operations',
                'host_phone': '+8801811111111',
                'host_email': 'sam@example.com',
            })

        self.stdout.write(self.style.SUCCESS('Demo data created. Login: reception / pass12345'))
