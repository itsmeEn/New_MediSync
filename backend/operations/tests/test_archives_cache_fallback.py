from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from django.utils import timezone
from rest_framework.test import APIClient

from backend.operations.models import PatientAssessmentArchive


class ArchiveCacheFallbackTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            email="patient1@example.com",
            password="Pass1234",
            full_name="Patient One",
            role="patient",
            hospital_name="Test Hospital",
            verification_status="approved",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        PatientAssessmentArchive.objects.create(
            user=self.user,
            assessment_type="intake",
            medical_condition="test",
            assessment_data={"archived": True, "note": "ok"},
            last_assessed_at=timezone.now(),
            hospital_name="Test Hospital",
        )

    @patch("backend.operations.archive_views.cache.get", side_effect=ConnectionRefusedError("redis down"))
    @patch("backend.operations.archive_views.cache.set", side_effect=ConnectionRefusedError("redis down"))
    def test_archive_list_works_when_cache_unavailable(self, *_):
        url = reverse("archive_list")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(isinstance(resp.json(), list) or "error" not in resp.json())

    @patch("backend.operations.archive_views.cache.get", side_effect=ConnectionRefusedError("redis down"))
    @patch("backend.operations.archive_views.cache.set", side_effect=ConnectionRefusedError("redis down"))
    def test_archive_detail_works_when_cache_unavailable(self, *_):
        record = PatientAssessmentArchive.objects.first()
        url = reverse("archive_detail", args=[record.id])
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data.get("patient_id"), self.user.id)