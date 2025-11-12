# Medical Request Test Results

Scope
- Backend unit/integration tests for medical request creation and lifecycle.
- Performance smoke test via concurrent request creation.

Environment
- Django/DRF backend (local dev settings)
- Database: SQLite (test) / same as project default

Results Summary
- Create default request: PASS
- Doctor reception (role-scoped list): PASS
- Create with explicit urgency (high): PASS
- Purpose invalid type validation: PASS (400 with field error)
- Approve then deliver: PASS (approve=200, deliver=200)
- Role restriction on approve (patient): PASS (403)

Performance Smoke
- Concurrent 25 requests with 10 workers: PASS
- Sample result: `Created 25/25 requests concurrently in 1.8s; failures=0`

Artifacts
- Test module: `backend/operations/tests/test_medical_requests.py`
- Load script: `scripts/load_test_medical_requests.py`

Metrics
- Average create latency (local): ~70–120ms/request (indicative only)
- No observed DB lock contention at this scale

Notes
- For realistic throughput and latency, run on staging with Locust/k6 and production-like DB.