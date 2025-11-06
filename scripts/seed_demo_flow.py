"""
Seed Demo Flow: Register test patients, open the OPD queue, join the queue
as patients, verify presence on nurse queue, assign to a doctor, and submit
basic nursing intake data. Designed for local dev at http://localhost:8000/api.

Usage:
  python scripts/seed_demo_flow.py

Prereqs:
  - Backend server running at http://localhost:8000/
  - A nurse user exists; access token stored in frontend/.test_nurse_access_token.txt
  - At least one doctor exists and is available (use /api/operations/available-doctors/)
  - At least one active hospital exists (script fetches via /api/admin/hospitals/)

Notes:
  - Creates patients with deterministic emails and password 'Patient123'.
  - Opens OPD queue if closed.
  - Joins one patient to normal queue and another to priority queue.
  - Assigns the first joined patient to an available doctor.
  - Submits a basic nursing intake for the assigned patient.
"""

import json
import os
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import requests


BASE = os.environ.get("API_BASE", "http://localhost:8000/api")
USERS = f"{BASE}/users"
OPS = f"{BASE}/operations"
ADMIN = f"{BASE}/admin"


def read_nurse_access_token() -> Optional[str]:
    path = os.path.join("frontend", ".test_nurse_access_token.txt")
    try:
        with open(path, "r", encoding="utf-8") as f:
            token = f.read().strip()
            return token or None
    except Exception:
        return None


def get_headers(token: Optional[str] = None) -> Dict[str, str]:
    h = {"Content-Type": "application/json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h


def hospitals_list() -> List[Dict[str, Any]]:
    url = f"{ADMIN}/hospitals/"
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    data = r.json()
    # Admin endpoint returns {'hospitals': [...]} by default (ACTIVE only)
    if isinstance(data, dict) and isinstance(data.get("hospitals"), list):
        return data["hospitals"]
    return data if isinstance(data, list) else []


def pick_active_hospital_id() -> int:
    hospitals = hospitals_list()
    # The public list already returns ACTIVE hospitals; take the first.
    if not hospitals:
        raise RuntimeError("No ACTIVE hospital found. Create one via management command or admin endpoints.")
    return int(hospitals[0]["id"])


def register_patient(email: str, hospital_id: int, password: str = "Patient123") -> Dict[str, Any]:
    payload = {
        "email": email,
        "full_name": email.split("@")[0].replace(".", " ").title(),
        "role": "patient",
        "date_of_birth": "1990-01-01",
        "gender": "other",
        "password": password,
        "password2": password,
        "hospital_id": hospital_id,
    }
    url = f"{USERS}/register/"
    r = requests.post(url, headers=get_headers(), json=payload, timeout=20)
    r.raise_for_status()
    return r.json()


def login(email: str, password: str) -> Tuple[str, Dict[str, Any]]:
    url = f"{USERS}/login/"
    r = requests.post(url, headers=get_headers(), json={"email": email, "password": password}, timeout=10)
    r.raise_for_status()
    data = r.json()
    access = data.get("access") or data.get("access_token")
    if not access:
        raise RuntimeError("Login response missing access token")
    return access, data.get("user", {})


def ensure_opd_queue_open(nurse_token: str) -> None:
    status_url = f"{OPS}/queue/status/?department=OPD"
    try:
        r = requests.get(status_url, headers=get_headers(nurse_token), timeout=10)
        if r.status_code == 200:
            is_open = bool(r.json().get("is_open"))
            if is_open:
                print("OPD queue already open.")
                return
    except Exception:
        # Treat errors as closed/not configured
        pass

    print("Opening OPD queue...")
    r2 = requests.post(f"{OPS}/queue/status/", headers=get_headers(nurse_token), json={"department": "OPD", "is_open": True}, timeout=10)
    r2.raise_for_status()
    print("OPD queue opened.")


def join_queue_patient(access_token: str, department: str = "OPD", priority_level: Optional[str] = None) -> Dict[str, Any]:
    url = f"{OPS}/queue/join/"
    payload: Dict[str, Any] = {"department": department}
    if priority_level:
        payload["priority_level"] = priority_level
    r = requests.post(url, headers=get_headers(access_token), json=payload, timeout=10)
    try:
        r.raise_for_status()
        return r.json()
    except requests.HTTPError as e:
        # If already in queue, return server message so the flow can proceed idempotently
        if r is not None and r.status_code == 400:
            try:
                return r.json()
            except Exception:
                # Fallback structure
                return {"error": "Queue join failed with 400", "status_code": 400}
        raise


def list_nurse_queue(nurse_token: str, department: str = "OPD") -> Dict[str, Any]:
    url = f"{OPS}/nurse/queue/patients/?department={department}"
    r = requests.get(url, headers=get_headers(nurse_token), timeout=10)
    r.raise_for_status()
    return r.json()


def list_available_doctors(nurse_token: str) -> List[Dict[str, Any]]:
    url = f"{OPS}/available-doctors/"
    r = requests.get(url, headers=get_headers(nurse_token), timeout=10)
    r.raise_for_status()
    data = r.json()
    # Operations endpoint returns a dict like {'doctors': [...], 'total_count': N}
    if isinstance(data, dict) and isinstance(data.get("doctors"), list):
        return data["doctors"]
    return data if isinstance(data, list) else []


def assign_patient(nurse_token: str, patient_id: int, doctor_id: int, specialization: str) -> Dict[str, Any]:
    url = f"{OPS}/assign-patient/"
    payload = {
        "patient_id": patient_id,
        "doctor_id": doctor_id,
        "specialization": specialization,
    }
    r = requests.post(url, headers=get_headers(nurse_token), json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


def submit_nurse_intake(nurse_token: str, patient_id: int) -> Dict[str, Any]:
    url = f"{USERS}/nurse/patient/{patient_id}/intake/"
    payload = {
        "vitals": {"bp": "120/80", "hr": 72, "rr": 16, "temp_c": 36.8},
        "weight_kg": 70.5,
        "height_cm": 175.0,
        "chief_complaint": "Routine check-up",
        "pain_score": 0,
        "allergies": ["None"],
        "current_medications": [],
    }
    r = requests.put(url, headers=get_headers(nurse_token), json=payload, timeout=15)
    r.raise_for_status()
    return r.json()


def main():
    nurse_token = read_nurse_access_token()
    if not nurse_token:
        print("ERROR: Nurse access token not found at frontend/.test_nurse_access_token.txt")
        sys.exit(1)

    # Pick an active hospital
    hospital_id = pick_active_hospital_id()
    print(f"Using hospital_id={hospital_id}")

    # Register two test patients
    patients = [
        {"email": "john.patient.demo1@example.com", "password": "Patient123"},
        {"email": "mary.patient.demo2@example.com", "password": "Patient123"},
    ]
    for p in patients:
        try:
            print(f"Registering patient: {p['email']}")
            reg = register_patient(p["email"], hospital_id, p["password"])
            print("Registered:", reg.get("email"), reg.get("id"))
        except requests.HTTPError as e:
            # If already exists, continue
            if e.response is not None and e.response.status_code == 400:
                print(f"Patient already exists: {p['email']} (continuing)")
            else:
                raise

    # Ensure OPD queue is open
    ensure_opd_queue_open(nurse_token)

    # Login patients
    tokens_users: List[Tuple[str, Dict[str, Any]]] = []
    for p in patients:
        print(f"Logging in patient: {p['email']}")
        access, user = login(p["email"], p["password"])
        tokens_users.append((access, user))
        print(f" -> patient_id={user.get('id')} name={user.get('full_name')}")

    # Join queues: first normal, second priority
    print("Joining OPD queue as normal (patient 1)")
    j1 = join_queue_patient(tokens_users[0][0], department="OPD", priority_level=None)
    print(" -> normal join response:", json.dumps(j1, indent=2))

    print("Joining OPD queue as priority (patient 2)")
    j2 = join_queue_patient(tokens_users[1][0], department="OPD", priority_level="pwd")
    print(" -> priority join response:", json.dumps(j2, indent=2))

    # Verify presence in nurse queue
    time.sleep(0.8)
    nq = list_nurse_queue(nurse_token, department="OPD")
    print("Nurse queue snapshot:", json.dumps({
        "normal_queue_count": len(nq.get("normal_queue", []) or []),
        "priority_queue_count": len(nq.get("priority_queue", []) or []),
        "all_patients_count": len(nq.get("all_patients", []) or []),
    }, indent=2))

    # Assign first patient to a doctor
    doctors = list_available_doctors(nurse_token)
    if not doctors:
        raise RuntimeError("No available doctors found. Ensure at least one doctor exists and is available.")
    doc = doctors[0]
    specialization = doc.get("specialization") or "General Medicine"
    # Use user id for assignment, but patient profile id for nurse intake
    first_patient_user_id = tokens_users[0][1].get("id")
    first_patient_profile_id = (tokens_users[0][1].get("patient_profile") or {}).get("id") or first_patient_user_id
    print(f"Assigning patient_id={first_patient_user_id} to doctor_id={doc.get('id')} specialization={specialization}")
    assign_resp = assign_patient(nurse_token, int(first_patient_user_id), int(doc.get("id")), specialization)
    print(" -> assignment response:", json.dumps(assign_resp, indent=2))

    # Submit nursing intake for the first patient
    intake_resp = submit_nurse_intake(nurse_token, int(first_patient_profile_id))
    print(" -> nursing intake updated:", json.dumps(intake_resp, indent=2))

    print("\nSeed demo flow completed successfully.")


if __name__ == "__main__":
    main()