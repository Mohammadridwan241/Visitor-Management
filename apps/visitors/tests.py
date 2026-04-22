from datetime import timedelta
from tempfile import TemporaryDirectory

from django.contrib.auth import get_user_model
from django.test import override_settings
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from .models import Visit
from .services import create_visit


def visit_payload(**overrides):
    payload = {
        'visitor_name': 'Jane Visitor',
        'visitor_phone': '+8801711111111',
        'visitor_email': 'jane@example.com',
        'visitor_company': 'Acme Ltd',
        'purpose_of_visit': 'Project meeting',
        'visit_date': timezone.localdate() + timedelta(days=1),
        'visit_time': '10:30',
        'host_name': 'Sam Host',
        'host_department': 'Operations',
        'host_phone': '+8801811111111',
        'host_email': 'sam@example.com',
    }
    payload.update(overrides)
    return payload


class TempMediaMixin:
    @classmethod
    def setUpClass(cls):
        cls._media_dir = TemporaryDirectory()
        cls._override = override_settings(MEDIA_ROOT=cls._media_dir.name)
        cls._override.enable()
        super().setUpClass()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls._override.disable()
        cls._media_dir.cleanup()


class VisitWorkflowTests(TempMediaMixin, TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='reception',
            email='reception@example.com',
            password='pass12345',
            full_name='Reception User',
            role='RECEPTIONIST',
        )

    def test_visitor_registration_creates_qr_token_and_image(self):
        visit = create_visit(visit_payload())

        self.assertTrue(visit.reference_no.startswith('VIS-'))
        self.assertTrue(visit.qr_token)
        self.assertTrue(visit.qr_code_image)
        self.assertEqual(visit.status, Visit.Status.PENDING)

    def test_qr_tokens_are_unique(self):
        first = create_visit(visit_payload(visitor_phone='1'))
        second = create_visit(visit_payload(visitor_phone='2'))

        self.assertNotEqual(first.qr_token, second.qr_token)

    def test_check_in_success(self):
        visit = create_visit(visit_payload())

        visit.perform_check_in(self.user)
        visit.refresh_from_db()

        self.assertEqual(visit.status, Visit.Status.CHECKED_IN)
        self.assertIsNotNone(visit.checked_in_at)
        self.assertEqual(visit.checked_in_by, self.user)

    def test_check_in_fails_after_checked_in(self):
        visit = create_visit(visit_payload())
        visit.perform_check_in(self.user)

        with self.assertRaises(Exception):
            visit.perform_check_in(self.user)

    def test_checkout_success(self):
        visit = create_visit(visit_payload())
        visit.perform_check_in(self.user)
        visit.perform_check_out(self.user)
        visit.refresh_from_db()

        self.assertEqual(visit.status, Visit.Status.CHECKED_OUT)
        self.assertIsNotNone(visit.checked_out_at)
        self.assertEqual(visit.checked_out_by, self.user)

    def test_checkout_fails_before_check_in(self):
        visit = create_visit(visit_payload())

        with self.assertRaises(Exception):
            visit.perform_check_out(self.user)


class VisitAPITests(TempMediaMixin, TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            username='reception',
            email='reception@example.com',
            password='pass12345',
            full_name='Reception User',
            role='RECEPTIONIST',
        )

    def test_public_registration_api(self):
        response = self.client.post(reverse('api-visit-register'), visit_payload(), format='json')

        self.assertEqual(response.status_code, 201)
        self.assertIn('qr_token', response.data)

    def test_qr_lookup_requires_authentication(self):
        visit = create_visit(visit_payload())

        response = self.client.get(reverse('api-visit-qr', kwargs={'token': visit.qr_token}))

        self.assertEqual(response.status_code, 401)

    def test_qr_lookup_success(self):
        visit = create_visit(visit_payload())
        self.client.force_authenticate(self.user)

        response = self.client.get(reverse('api-visit-qr', kwargs={'token': visit.qr_token}))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['reference_no'], visit.reference_no)

    def test_check_in_api(self):
        visit = create_visit(visit_payload())
        self.client.force_authenticate(self.user)

        response = self.client.post(reverse('api-visit-check-in', kwargs={'pk': visit.pk}), {}, format='json')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], Visit.Status.CHECKED_IN)

    def test_checkout_api_fails_before_check_in(self):
        visit = create_visit(visit_payload())
        self.client.force_authenticate(self.user)

        response = self.client.post(reverse('api-visit-check-out', kwargs={'pk': visit.pk}), {}, format='json')

        self.assertEqual(response.status_code, 400)
