# QA Checklist: Medical Request Functionality

Regression Testing
- Patient creates medical certificate request (201)
- Patient creates full records request (201)
- Doctor lists patient requests (200, contains created IDs)
- Approve pending request (200)
- Deliver approved request (200)
- Reject request with reason (200)
- Add doctor notes (200) and mark processing (200)

Error Handling & Edge Cases
- Purpose non-string -> 400 with field error
- Missing patient_id -> 400 validation error
- Patient approves/delivers -> 403 forbidden
- Deliver while pending -> 400

Security Review
- Verify RBAC in approve/deliver/reject endpoints (doctor-only)
- Ensure only patient sees their own created requests on GET
- Confirm notifications target only intended user groups

Compliance
- Sensitive fields not exposed unintentionally in serializers
- PDF generation uses encryption (`encrypt_pdf_aes256`) before transmission
- Transmission audit logs recorded via `ArchiveAccessLog`

Sign-offs
- Technical lead review completed
- Medical stakeholder validation completed