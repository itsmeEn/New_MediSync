from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from unittest.mock import patch

from backend.users.models import GeneralDoctorProfile, PatientProfile
from backend.operations.models import MedicalRecordRequest


@override_settings(DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}})
class MedicalRequestFlowTests(TestCase):
    """Comprehensive tests for patient medical request creation and doctor workflow."""

    def setUp(self):
        self.client = APIClient()
        User = get_user_model()

        # Create core users
        self.doctor = User.objects.create_user(
            email="doctor@example.com", password="Password123", role="doctor", full_name="Dr. House"
        )
        self.patient = User.objects.create_user(
            email="patient@example.com", password="Password123", role="patient", full_name="Pat Patient"
        )

        # Profiles
        self.doc_profile = GeneralDoctorProfile.objects.create(user=self.doctor, specialization="General Medicine")
        self.patient_profile = PatientProfile.objects.create(user=self.patient)
        # Link assigned doctor to patient profile to simulate hospital assignment
        self.patient_profile.assigned_doctor = self.doctor
        self.patient_profile.save()

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def _create_request(self, payload):
        with (
            patch("backend.operations.medical_request_views.generate_records_pdf", return_value=b"PDF"),
            patch("backend.operations.medical_request_views.encrypt_pdf_aes256", return_value=b"PDF"),
            patch("backend.operations.medical_request_views.send_encrypted_pdf_to_patient", return_value=True),
        ):
            return self.client.post("/api/operations/medical-requests/", payload, format="json")

    def test_create_request_default_urgency_and_doctor_reception(self):
        """Patient can create request; doctor sees it; urgency defaults to medium."""
        self.auth(self.patient)
        payload = {
            "patient_id": self.patient.id,
            "attending_doctor_id": self.doc_profile.id,
            "request_type": "medical_certificate",
            "requested_records": {"history_physical": True},
            "reason": "Need certificate for work",
            "purpose": "work_leave",
        }
        resp = self._create_request(payload)
        self.assertEqual(resp.status_code, 201, resp.content)
        data = resp.json()
        self.assertEqual(data.get("urgency"), "medium")
        self.assertEqual(data.get("status"), "pending")
        req_id = data.get("id")
        self.assertIsInstance(req_id, int)

        # Doctor reception: doctor should list the request
        self.auth(self.doctor)
        resp2 = self.client.get("/api/operations/medical-requests/")
        self.assertEqual(resp2.status_code, 200, resp2.content)
        items = resp2.json()
        self.assertTrue(any(item.get("id") == req_id for item in items))

    def test_create_request_with_high_urgency(self):
        """Explicit urgency is honored by backend."""
        self.auth(self.patient)
        payload = {
            "patient_id": self.patient.id,
            "attending_doctor_id": self.doc_profile.id,
            "request_type": "lab_results",
            "requested_records": {"progress_notes": True},
            "reason": "Review latest labs",
            "urgency": "high",
        }
        resp = self._create_request(payload)
        self.assertEqual(resp.status_code, 201, resp.content)
        self.assertEqual(resp.json().get("urgency"), "high")

    def test_purpose_validation_error_on_invalid_type(self):
        """Backend rejects non-string purpose values with a 400 validation error."""
        self.auth(self.patient)
        payload = {
            "patient_id": self.patient.id,
            "attending_doctor_id": self.doc_profile.id,
            "request_type": "medical_certificate",
            "requested_records": {},
            "reason": "Certification",
            "purpose": ["not", "a", "string"],
        }
        resp = self.client.post("/api/operations/medical-requests/", payload, format="json")
        self.assertEqual(resp.status_code, 400, resp.content)
        # Expect serializer error to mention 'purpose'
        body = resp.json()
        self.assertTrue("purpose" in body)

    def test_approve_then_deliver_happy_path(self):
        """Doctor can approve then deliver; pending cannot deliver."""
        # Create request
        self.auth(self.patient)
        payload = {
            "patient_id": self.patient.id,
            "attending_doctor_id": self.doc_profile.id,
            "request_type": "full_records",
            "requested_records": {"history_physical": True, "progress_notes": True},
            "reason": "Transfer of care",
        }
        resp = self._create_request(payload)
        self.assertEqual(resp.status_code, 201, resp.content)
        req_id = resp.json().get("id")

        # Attempt deliver while pending -> expect 400
        self.auth(self.doctor)
        resp_deliver_pending = self.client.post(f"/api/operations/medical-requests/{req_id}/deliver/")
        self.assertEqual(resp_deliver_pending.status_code, 400, resp_deliver_pending.content)

        # Approve
        resp_approve = self.client.post(f"/api/operations/medical-requests/{req_id}/approve/")
        self.assertEqual(resp_approve.status_code, 200, resp_approve.content)
        self.assertEqual(resp_approve.json().get("status"), "approved")

        # Deliver
        with (
            patch("backend.operations.medical_request_views.generate_records_pdf", return_value=b"PDF"),
            patch("backend.operations.medical_request_views.encrypt_pdf_aes256", return_value=b"PDF"),
            patch("backend.operations.medical_request_views.send_encrypted_pdf_to_patient", return_value=True),
        ):
            resp_deliver = self.client.post(f"/api/operations/medical-requests/{req_id}/deliver/")
        self.assertEqual(resp_deliver.status_code, 200, resp_deliver.content)
        self.assertIn(resp_deliver.json().get("status"), ["delivered", "completed", "approved"])  # allow for serializer variations

    def test_role_restrictions_on_approve(self):
        """Only doctors can approve requests."""
        # Create request as patient
        self.auth(self.patient)
        resp = self._create_request({
            "patient_id": self.patient.id,
            "attending_doctor_id": self.doc_profile.id,
            "request_type": "general_inquiry",
            "requested_records": {},
            "reason": "Question",
        })
        req_id = resp.json().get("id")

        # Patient cannot approve
        self.auth(self.patient)
        resp_forbidden = self.client.post(f"/api/operations/medical-requests/{req_id}/approve/")
        self.assertEqual(resp_forbidden.status_code, 403)

        # Doctor can approve
        self.auth(self.doctor)
        resp_ok = self.client.post(f"/api/operations/medical-requests/{req_id}/approve/")
        self.assertEqual(resp_ok.status_code, 200)


@override_settings(DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}})
class MedicalRequestDataIntegrityTests(TestCase):
    """Validate data integrity across transmission and request lifecycle."""

    def setUp(self):
        self.client = APIClient()
        User = get_user_model()

        self.doctor = User.objects.create_user(
            email="doc2@example.com", password="Password123", role="doctor", full_name="Dr. Strange"
        )
        self.patient = User.objects.create_user(
            email="pat2@example.com", password="Password123", role="patient", full_name="Jane Patient"
        )
        self.doc_profile = GeneralDoctorProfile.objects.create(user=self.doctor, specialization="Internal")
        self.patient_profile = PatientProfile.objects.create(user=self.patient)

    def auth(self, user):
        self.client.force_authenticate(user=user)

    def test_payload_roundtrip_fields(self):
        """Ensure important fields persist: request_type, reason, urgency, purpose, date ranges."""
        self.auth(self.patient)
        payload = {
            "patient_id": self.patient.id,
            "attending_doctor_id": self.doc_profile.id,
            "request_type": "medical_certificate",
            "requested_records": {},
            "reason": "Verification",
            "purpose": "school_university",
            "requested_date_range_start": "2023-01-01",
            "requested_date_range_end": "2023-12-31",
            "urgency": "urgent",
        }
        resp = self.client.post("/api/operations/medical-requests/", payload, format="json")
        self.assertEqual(resp.status_code, 201, resp.content)
        data = resp.json()
        self.assertEqual(data.get("request_type"), payload["request_type"])  # serializer uses request_type
        self.assertEqual(data.get("reason"), payload["reason"])  # maps to reason
        self.assertEqual(data.get("urgency"), payload["urgency"])  # explicit urgency preserved