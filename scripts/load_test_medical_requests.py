"""
Simple concurrent load test for medical requests.

Usage:
  - Ensure Django settings are configured (run from project root).
  - This script bootstraps Django and uses DRF's APIClient to simulate
    multiple patients creating requests concurrently.

Notes:
  - Intended for local performance smoke checks; not a full benchmark.
  - For production-grade load testing, integrate Locust or k6.
"""

import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")
import django  # noqa: E402

django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from rest_framework.test import APIClient  # noqa: E402
from backend.users.models import GeneralDoctorProfile, PatientProfile  # noqa: E402


def setup_users():
    User = get_user_model()
    doctor = User.objects.create_user(email="perfdoctor@example.com", password="Password123", role="doctor", full_name="Perf Doc")
    doc_profile = GeneralDoctorProfile.objects.create(user=doctor, specialization="General")
    patients = []
    for i in range(25):
        u = User.objects.create_user(email=f"perfpatient{i}@example.com", password="Password123", role="patient", full_name=f"Perf Patient {i}")
        PatientProfile.objects.create(user=u)
        patients.append(u)
    return doctor, doc_profile, patients


def create_request(client: APIClient, patient, doctor_profile_id: int, idx: int):
    client.force_authenticate(user=patient)
    payload = {
        "patient_id": patient.id,
        "attending_doctor_id": doctor_profile_id,
        "request_type": "lab_results" if idx % 2 == 0 else "full_records",
        "requested_records": {"progress_notes": True},
        "reason": "Load test",
    }
    resp = client.post("/operations/medical-requests/", payload, format="json")
    return resp.status_code


def main():
    doctor, doc_profile, patients = setup_users()
    client = APIClient()
    start = time.time()
    results = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(create_request, APIClient(), p, doc_profile.id, i) for i, p in enumerate(patients)]
        for fut in as_completed(futures):
            results.append(fut.result())
    duration = time.time() - start
    ok = sum(1 for r in results if r == 201)
    fail = len(results) - ok
    print(f"Created {ok}/{len(results)} requests concurrently in {duration:.2f}s; failures={fail}")


if __name__ == "__main__":
    main()