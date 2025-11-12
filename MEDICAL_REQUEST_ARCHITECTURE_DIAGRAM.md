# Medical Request Architecture (Updated)

```
Patient (SPA)         Backend (DRF)               Realtime (Channels)          Doctor (SPA)
    |                      |                                 |                      |
    | POST /operations/medical-requests/                     |                      |
    |--------------------->|  CreateMedicalRecordRequest     |                      |
    |                      |  -> validate (serializer)       |                      |
    |                      |  -> persist (model)             |                      |
    |                      |  -> notify via group_send ------+----> messaging_{uid} |
    |                      |                                 |                      |
    |   201 + request JSON |                                 |                      |
    |<---------------------|                                 |                      |
    |                      |                                 |                      |
    |                      |  Doctor actions: approve/deliver/reject/add-notes      |
    |                      |  POST /operations/medical-requests/{id}/approve        |
    |                      |  POST /operations/medical-requests/{id}/deliver        |
    |                      |  POST /operations/medical-requests/{id}/reject         |
    |                      |  POST /operations/medical-requests/{id}/add-notes      |
    |                      |                                 |                      |
    | GET /operations/medical-requests/ (role-scoped) -----------------------------> |
    |                                                                               |
```

Key Components
- `MedicalRecordRequest` model stores request lifecycle.
- `CreateMedicalRecordRequestSerializer` enforces input types and defaults.
- `medical_request_views.py` handles creation and doctor actions.
- Channels broadcasts realtime notifications to doctor/nurse/patient groups.

Data Integrity
- `requested_records` JSON field carries requested items.
- `urgency` defaults to `medium` when omitted.
- `purpose` is a string; invalid types are rejected by serializer.