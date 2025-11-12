# Medical Request Rollback Procedures

Trigger Conditions
- Integration errors affecting patient request submission or doctor reception.
- Performance degradation under normal or peak loads.
- Security concerns in new data flows.

Rollback Steps
1. Disable deployments impacting medical request endpoints.
2. Revert frontend change if needed (restore `urgency` UI) or keep omission since backend defaults to `medium`.
3. Backend: no code changes introduced; tests/scripts/docs only. If a server-side regression is detected, revert to last known good image/tag.
4. Clear problematic queued tasks (if any) and monitor Channels groups for stalled notifications.
5. Verify health by running:
   - `python manage.py test backend/operations/tests/test_medical_requests.py`
   - `curl -sS http://localhost:8000/operations/verification-status/`

Post-Rollback Verification
- Patients can create requests (201) and see them in their list.
- Doctors can list, approve, and deliver requests.
- Notifications are delivered to expected groups.

Communication & Sign-off
- Notify technical stakeholders of rollback and impact.
- Confirm with medical stakeholders that request operations are restored.
- Schedule root-cause analysis and corrective actions.