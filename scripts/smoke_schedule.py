import json
import sys
import time
import uuid
from urllib import request
from urllib.error import HTTPError, URLError

BASE = "http://127.0.0.1:8001/api"

def post_json(url: str, payload: dict, headers: dict = None):
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json", **(headers or {})}, method="POST")
    try:
        with request.urlopen(req) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print("http_error", e.code, body)
        raise
    except URLError as e:
        print("url_error", str(e))
        raise

def main():
    ts = str(int(time.time()))
    suffix = uuid.uuid4().hex[:6]
    doc_email = f"doctor.smoke.{ts}.{suffix}@example.com"
    pat_email = f"patient.smoke.{ts}.{suffix}@example.com"

    # Register doctor
    try:
        post_json(f"{BASE}/users/register/", {
            "email": doc_email,
            "full_name": "Dr Smoke",
            "role": "doctor",
            "password": "Test1234!",
            "password2": "Test1234!",
            "date_of_birth": "1980-01-01",
            "gender": "male",
            "license_number": f"DOC{ts}{suffix}",
            "specialization": "General Medicine",
        })
    except Exception as e:
        print("doctor_register_error", e)
        # continue; doctor may already exist

    # Register patient
    try:
        post_json(f"{BASE}/users/register/", {
            "email": pat_email,
            "full_name": "Patient Smoke",
            "role": "patient",
            "password": "Test1234!",
            "password2": "Test1234!",
            "date_of_birth": "1990-01-02",
            "gender": "female",
        })
    except Exception as e:
        print("patient_register_error", e)

    # Login patient
    try:
        login = post_json(f"{BASE}/users/login/", {"email": pat_email, "password": "Test1234!"})
        access = login.get("access", "")
        print("access_len", len(access))
    except Exception as e:
        print("patient_login_error", e)
        return 1

    # Schedule appointment
    try:
        from datetime import datetime, timedelta
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        resp = post_json(f"{BASE}/operations/appointments/schedule/", {
            "type": "lab-test",
            "date": date,
            "time": "18:30",
            "reason": "Lab test request",
        }, headers={"Authorization": f"Bearer {access}"})
        print("schedule_message", resp.get("message"))
        appt = resp.get("appointment", {}) or {}
        print("appointment_type", appt.get("appointment_type"))
        print("appointment_id", appt.get("appointment_id"))
        return 0
    except Exception as e:
        print("schedule_error", e)
        return 2

if __name__ == "__main__":
    sys.exit(main())