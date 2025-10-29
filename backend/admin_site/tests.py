from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile

from backend.admin_site.models import AdminUser, Hospital, VerificationRequest
from backend.users.models import User


class AdminSiteAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_hospitals_list_defaults_to_active(self):
        # Create hospitals with different statuses
        active_hospital = Hospital.objects.create(
            official_name="General Hospital",
            address="123 Health St",
            license_id="LIC-0001",
            license_document=SimpleUploadedFile('lic1.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.ACTIVE
        )
        Hospital.objects.create(
            official_name="Pending Medical Center",
            address="456 Wellness Ave",
            license_id="LIC-0002",
            license_document=SimpleUploadedFile('lic2.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.PENDING
        )
        Hospital.objects.create(
            official_name="Suspended Clinic",
            address="789 Care Rd",
            license_id="LIC-0003",
            license_document=SimpleUploadedFile('lic3.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.SUSPENDED
        )

        url = reverse('hospitals_list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        hospitals = data.get('hospitals', [])
        # Only active hospital should be returned by default
        self.assertEqual(len(hospitals), 1)
        self.assertEqual(hospitals[0]['id'], active_hospital.id)
        self.assertEqual(hospitals[0]['official_name'], active_hospital.official_name)
        self.assertEqual(hospitals[0]['address'], active_hospital.address)

    def test_accept_verification_hospital_mismatch_rejected(self):
        # Create admin user and JWT
        admin = AdminUser.objects.create_user(
            email="admin@medisync.local",
            password="AdminPass123!",
            full_name="Admin User",
            is_active=True,
            is_email_verified=True,
        )
        refresh = RefreshToken.for_user(admin)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Create active hospital that DOES NOT match user's hospital
        Hospital.objects.create(
            official_name="General Hospital",
            address="123 Health St",
            license_id="LIC-1001",
            license_document=SimpleUploadedFile('lic1001.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.ACTIVE
        )

        # Create user and verification request with mismatching hospital
        user = User.objects.create_user(
            email="doc@example.com",
            password="DocPass123!",
            full_name="Doctor Who",
            role="doctor",
            hospital_name="Other Hospital",
            hospital_address="999 Different Rd",
        )
        verification = VerificationRequest.objects.create(
            user_email=user.email,
            user_full_name=user.full_name,
            user_role="doctor",
            status=VerificationRequest.Status.PENDING,
        )

        url = reverse('accept_verification', kwargs={"verification_id": verification.id})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Hospital mismatch', resp.json().get('error', ''))

    def test_accept_verification_hospital_match_approved(self):
        # Create admin user and JWT
        admin = AdminUser.objects.create_user(
            email="admin2@medisync.local",
            password="AdminPass123!",
            full_name="Admin Two",
            is_active=True,
            is_email_verified=True,
        )
        refresh = RefreshToken.for_user(admin)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Create active hospital that matches user's hospital
        hospital = Hospital.objects.create(
            official_name="Match Hospital",
            address="321 Health Blvd",
            license_id="LIC-2001",
            license_document=SimpleUploadedFile('lic2001.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.ACTIVE
        )

        # Create user and verification request with matching hospital
        user = User.objects.create_user(
            email="nurse@example.com",
            password="NursePass123!",
            full_name="Nurse Joy",
            role="nurse",
            hospital_name=hospital.official_name,
            hospital_address=hospital.address,
        )
        verification = VerificationRequest.objects.create(
            user_email=user.email,
            user_full_name=user.full_name,
            user_role="nurse",
            status=VerificationRequest.Status.PENDING,
        )

        url = reverse('accept_verification', kwargs={"verification_id": verification.id})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json().get('message'), 'Verification approved successfully')

    def test_hospital_activation_persists_and_visible_in_lists(self):
        # Create admin user and JWT
        admin = AdminUser.objects.create_user(
            email="admin3@medisync.local",
            password="AdminPass123!",
            full_name="Admin Three",
            is_active=True,
            is_email_verified=True,
        )
        refresh = RefreshToken.for_user(admin)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Create pending hospital and link to admin
        hospital = Hospital.objects.create(
            official_name="Activation Hospital",
            address="12 Activate Rd",
            license_id="LIC-3001",
            license_document=SimpleUploadedFile('lic3001.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.PENDING
        )
        admin.hospital = hospital
        admin.save()

        # Activate via API
        activation_url = reverse('hospital_activation')
        resp = self.client.post(activation_url, {'terms_accepted': True, 'data_verified': True}, format='json')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data['hospital']['status'], Hospital.Status.ACTIVE)

        # Verify appears in public hospitals list (defaults to ACTIVE)
        list_url = reverse('hospitals_list')
        # Clear auth header for public endpoint to avoid 401 from failed auth
        self.client.credentials()
        resp_list = self.client.get(list_url)
        self.assertEqual(resp_list.status_code, 200)
        hospitals = resp_list.json().get('hospitals', [])
        ids = [h['id'] for h in hospitals]
        self.assertIn(hospital.id, ids)

        # Verify appears in admin my hospitals with default ACTIVE filter
        my_url = reverse('admin_my_hospitals')
        # Restore auth for admin-scoped endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")
        resp_my = self.client.get(my_url)
        self.assertEqual(resp_my.status_code, 200)
        my_hospitals = resp_my.json().get('hospitals', [])
        my_ids = [h['id'] for h in my_hospitals]
        self.assertIn(hospital.id, my_ids)

    def test_hospitals_list_invalid_status_returns_400(self):
        url = reverse('hospitals_list')
        resp = self.client.get(url + '?status=unknown')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('Invalid status filter', resp.json().get('error', ''))

    def test_serve_verification_document_pdf_success(self):
        # Create active hospital and link to admin
        hospital = Hospital.objects.create(
            official_name="Doc Hospital",
            address="10 Care Way",
            license_id="LIC-4001",
            license_document=SimpleUploadedFile('lic4001.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.ACTIVE
        )
        admin = AdminUser.objects.create_user(
            email="admin-doc@medisync.local",
            password="AdminPass123!",
            full_name="Admin Doc",
            is_active=True,
            is_email_verified=True,
        )
        admin.hospital = hospital
        admin.hospital_registration_completed = True
        admin.save()
        refresh = RefreshToken.for_user(admin)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Create user under same hospital
        user = User.objects.create_user(
            email="doc2@example.com",
            password="DocPass123!",
            full_name="Doctor Two",
            role="doctor",
            hospital_name=hospital.official_name,
            hospital_address=hospital.address,
        )
        # Attach a PDF document
        pdf_content = b"%PDF-1.4 Mock PDF content"
        verification = VerificationRequest.objects.create(
            user_email=user.email,
            user_full_name=user.full_name,
            user_role="doctor",
            status=VerificationRequest.Status.PENDING,
            verification_document=SimpleUploadedFile('doc_verif.pdf', pdf_content, content_type='application/pdf')
        )

        url = reverse('serve_verification_document', kwargs={"verification_id": verification.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get('Content-Type'), 'application/pdf')
        self.assertIn('inline', resp.get('Content-Disposition', ''))

    def test_serve_verification_document_image_success(self):
        # Create active hospital and link to admin
        hospital = Hospital.objects.create(
            official_name="Image Hospital",
            address="20 Pixel Rd",
            license_id="LIC-4002",
            license_document=SimpleUploadedFile('lic4002.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.ACTIVE
        )
        admin = AdminUser.objects.create_user(
            email="admin-img@medisync.local",
            password="AdminPass123!",
            full_name="Admin Img",
            is_active=True,
            is_email_verified=True,
        )
        admin.hospital = hospital
        admin.hospital_registration_completed = True
        admin.save()
        refresh = RefreshToken.for_user(admin)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Create user under same hospital
        user = User.objects.create_user(
            email="nurse2@example.com",
            password="NursePass123!",
            full_name="Nurse Two",
            role="nurse",
            hospital_name=hospital.official_name,
            hospital_address=hospital.address,
        )
        # Attach a PNG document
        png_bytes = b"\x89PNG\r\n\x1a\n" + b"mock"
        verification = VerificationRequest.objects.create(
            user_email=user.email,
            user_full_name=user.full_name,
            user_role="nurse",
            status=VerificationRequest.Status.PENDING,
            verification_document=SimpleUploadedFile('nurse_verif.png', png_bytes, content_type='image/png')
        )

        url = reverse('serve_verification_document', kwargs={"verification_id": verification.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get('Content-Type'), 'image/png')
        self.assertIn('inline', resp.get('Content-Disposition', ''))

    def test_serve_verification_document_hospital_mismatch_forbidden(self):
        # Create admin with active hospital A
        admin_hospital = Hospital.objects.create(
            official_name="Admin Hospital",
            address="30 Admin Blvd",
            license_id="LIC-4003",
            license_document=SimpleUploadedFile('lic4003.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.ACTIVE
        )
        admin = AdminUser.objects.create_user(
            email="admin-mismatch@medisync.local",
            password="AdminPass123!",
            full_name="Admin Mismatch",
            is_active=True,
            is_email_verified=True,
        )
        admin.hospital = admin_hospital
        admin.hospital_registration_completed = True
        admin.save()
        refresh = RefreshToken.for_user(admin)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Create different active hospital B for user
        user_hospital = Hospital.objects.create(
            official_name="User Hospital",
            address="40 User St",
            license_id="LIC-4004",
            license_document=SimpleUploadedFile('lic4004.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.ACTIVE
        )
        user = User.objects.create_user(
            email="doc-mismatch@example.com",
            password="DocPass123!",
            full_name="Doctor Mismatch",
            role="doctor",
            hospital_name=user_hospital.official_name,
            hospital_address=user_hospital.address,
        )
        verification = VerificationRequest.objects.create(
            user_email=user.email,
            user_full_name=user.full_name,
            user_role="doctor",
            status=VerificationRequest.Status.PENDING,
            verification_document=SimpleUploadedFile('doc_mismatch.pdf', b'PDF', content_type='application/pdf')
        )

        url = reverse('serve_verification_document', kwargs={"verification_id": verification.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 403)
        self.assertIn('Hospital mismatch', resp.json().get('error', ''))

    def test_serve_verification_document_not_found(self):
        # Create active hospital and admin
        hospital = Hospital.objects.create(
            official_name="Empty Doc Hospital",
            address="50 Missing Rd",
            license_id="LIC-4005",
            license_document=SimpleUploadedFile('lic4005.pdf', b'PDF', content_type='application/pdf'),
            status=Hospital.Status.ACTIVE
        )
        admin = AdminUser.objects.create_user(
            email="admin-empty@medisync.local",
            password="AdminPass123!",
            full_name="Admin Empty",
            is_active=True,
            is_email_verified=True,
        )
        admin.hospital = hospital
        admin.hospital_registration_completed = True
        admin.save()
        refresh = RefreshToken.for_user(admin)
        access = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

        # Create user and verification without a document
        user = User.objects.create_user(
            email="nurse-empty@example.com",
            password="NursePass123!",
            full_name="Nurse Empty",
            role="nurse",
            hospital_name=hospital.official_name,
            hospital_address=hospital.address,
        )
        verification = VerificationRequest.objects.create(
            user_email=user.email,
            user_full_name=user.full_name,
            user_role="nurse",
            status=VerificationRequest.Status.PENDING,
        )

        url = reverse('serve_verification_document', kwargs={"verification_id": verification.id})
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 404)
        self.assertIn('Document not found', resp.json().get('error', ''))
