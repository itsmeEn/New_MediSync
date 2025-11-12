# MediSync Web Test Cases

- Version: 1.0.0
- Last Updated: 2025-11-11
- Module: Web (Quasar/Vue)
- Scope: Test planning and execution record for web application

## Template (Use for every test case)

### 1) Test Case Identification
- Test Case ID: `WEB-TC-XXX`
- Module: `Web`
- Priority: `High | Medium | Low`
- Related Requirement: short reference to design requirement or user story

### 2) Test Case Details
- Description: concise statement of what is being validated
- Pre-requisites: list all conditions (e.g., test data, credentials, environment)
- Post-requisites: expected system state after completion

### 3) Test Execution Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results (Pass/Fail) |
|---|---|---|---|---|---|

Notes:
- Keep each step atomic and verifiable.
- Include both positive and negative steps where applicable.
- Add screenshots for critical steps in `docs/images/web/<TC-ID>/`.

---

## WEB-TC-001 — User Registration (Doctor/Nurse/Patient)

### Identification
- Test Case ID: WEB-TC-001
- Module: Web
- Priority: High
- Related Requirement: Registration and profile creation with JWT issuance

### Details
- Description: Validate registration flow for doctor, nurse, and patient with required profile data; confirm JWT tokens are returned and role profiles created.
- Pre-requisites:
  - Backend running (`python manage.py runserver`)
  - DB migrated; SMTP configured or dev email backend
  - Browser: Chrome 120 / macOS 14
- Post-requisites: New user exists; role profile created; audit/log entries present.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results (Pass/Fail) |
|---|---|---|---|---|---|
| 1 | Open registration page `/#/register` | Registration form loads |  | Chrome 120 (macOS) |  |
| 2 | Submit valid doctor info | 201 Created; `access`, `refresh` tokens; `GeneralDoctorProfile` persisted |  | Chrome 120 (macOS) |  |
| 3 | Submit valid nurse info | 201 Created; `NurseProfile` persisted |  | Chrome 120 (macOS) |  |
| 4 | Submit valid patient info | 201 Created; `PatientProfile` persisted |  | Chrome 120 (macOS) |  |
| 5 | Negative: missing email | 400 with validation errors |  | Chrome 120 (macOS) |  |
| 6 | Negative: weak password | 400 with Django password validator errors |  | Chrome 120 (macOS) |  |
| 7 | Backend verification | User + profile rows exist |  | Admin panel / psql |  |

Screenshot placeholders: `docs/images/web/WEB-TC-001/step-2-success.png`

---

## WEB-TC-002 — Login Without 2FA (Patient)

### Identification
- Test Case ID: WEB-TC-002
- Module: Web
- Priority: High
- Related Requirement: JWT login for non-2FA users

### Details
- Description: Validate patient login issues JWT and grants access to protected pages.
- Pre-requisites: Patient account active; `two_factor_enabled=false`.
- Post-requisites: `access` token stored; page navigation permitted.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open `/#/login` | Login form visible |  | Chrome 120 |  |
| 2 | Enter valid patient credentials | 200 OK; `access`/`refresh` in response |  | Chrome 120 |  |
| 3 | Navigate to protected route | Page displays; API calls succeed with `Authorization` header |  | Chrome 120 |  |
| 4 | Negative: wrong password | 401 Unauthorized; error message |  | Chrome 120 |  |

---

## WEB-TC-003 — Login With 2FA (Doctor)

### Identification
- Test Case ID: WEB-TC-003
- Module: Web
- Priority: High
- Related Requirement: Email-based OTP 2FA for doctors

### Details
- Description: Validate 2FA flow—OTP challenge on login and token issuance after OTP verification.
- Pre-requisites: Doctor account with `two_factor_enabled=true`; email delivery reachable.
- Post-requisites: Access granted after OTP; audit logs for `login_otp_sent` and `login_otp_verified` (if applicable).

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Login with doctor credentials | 200 OK; prompt for OTP; OTP emailed |  | Chrome 120 |  |
| 2 | Enter correct OTP | 200 OK; tokens returned; redirect to dashboard |  | Chrome 120 |  |
| 3 | Negative: wrong OTP | 400/401 with invalid code |  | Chrome 120 |  |
| 4 | Negative: expired OTP (>5m) | 400/401 expired code |  | Chrome 120 |  |

Screenshots: `docs/images/web/WEB-TC-003/step-1-otp-prompt.png`, `.../step-2-verified.png`

---

## WEB-TC-004 — Doctor Analytics PDF Download

### Identification
- Test Case ID: WEB-TC-004
- Module: Web
- Priority: Medium
- Related Requirement: PDF report via `/analytics/pdf/?type=doctor`

### Details
- Description: Generate and download PDF from doctor analytics page.
- Pre-requisites: Authenticated doctor; analytics data available.
- Post-requisites: PDF file downloaded; content type `application/pdf`.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open `/#/doctor-predictive-analytics` | Page loads charts/cards |  | Chrome 120 |  |
| 2 | Click “Generate PDF Report” | API request returns blob |  | Chrome 120 |  |
| 3 | Verify filename and download | `doctor_analytics_report_<date>.pdf` saved |  | Chrome 120 |  |
| 4 | Negative: unauthenticated | 401 from endpoint |  | Chrome 120 |  |

---

## WEB-TC-005 — Secure Transmission Creation & Retrieval

### Identification
- Test Case ID: WEB-TC-005
- Module: Web
- Priority: High
- Related Requirement: `/operations/secure/transmissions` lifecycle

### Details
- Description: Create a secure transmission and verify payload fields; list and detail retrieval.
- Pre-requisites: Sender with public key registered; receiver doctor available; patient exists.
- Post-requisites: Transmission stored with `pending` status; `TransmissionAudit` entry present.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | POST payload to create transmission | 201 Created; fields persisted |  | Chrome 120 |  |
| 2 | GET list for receiver | Includes new item |  | Chrome 120 |  |
| 3 | GET detail | Returns cryptographic fields |  | Chrome 120 |  |
| 4 | Negative: missing `ciphertext_b64` | 400 validation error |  | Chrome 120 |  |

---

## WEB-TC-006 — Purge Medical Records (Admin/Doctor)

### Identification
- Test Case ID: WEB-TC-006
- Module: Web
- Priority: High
- Related Requirement: Secure purge with `PurgeAuditLog`

### Details
- Description: Validate purge operation with `dry_run` and actual purge; confirm non-PHI auditing.
- Pre-requisites: Verified admin/doctor; patient selected; MFA verification complete if required.
- Post-requisites: Sensitive fields cleared; audit log recorded with counts.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | POST `dry_run=true` | 200 OK; counts returned; no changes |  | Chrome 120 |  |
| 2 | POST actual purge | 200 OK; PHI cleared; audit created |  | Chrome 120 |  |
| 3 | Negative: unauthorized role | 403 Forbidden |  | Chrome 120 |  |

---

## WEB-TC-007 — Queue FIFO and Position Normalization

### Identification
- Test Case ID: WEB-TC-007
- Module: Web
- Priority: Medium
- Related Requirement: `QueueManagement` FIFO semantics

### Details
- Description: Validate queue ordering and position updates.
- Pre-requisites: Department queue populated.
- Post-requisites: Positions normalized and consistent.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Add patient A then B | B behind A |  | Chrome 120 |  |
| 2 | Mark A served | B becomes first |  | Chrome 120 |  |
| 3 | Negative: invalid department id | 400 error |  | Chrome 120 |  |

---

## WEB-TC-008 — Token Refresh Interceptor

### Identification
- Test Case ID: WEB-TC-008
- Module: Web
- Priority: Medium
- Related Requirement: Axios refresh on 401 non-auth endpoints

### Details
- Description: Validate access token expiration triggers refresh and retries; failure redirects to login.
- Pre-requisites: Valid refresh token in storage; access token expired.
- Post-requisites: Request retries with new token; or logout on refresh failure.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Call protected endpoint with expired access | 401 received; refresh called |  | Chrome 120 |  |
| 2 | Verify retry succeeds | 200 OK on retry |  | Chrome 120 |  |
| 3 | Negative: invalid refresh token | Redirect to login; storage cleared |  | Chrome 120 |  |

---

## Version Control
- Document Version: 1.0.0
- Last Updated: 2025-11-11
- Change Log:
  - 1.0.0 — Initial comprehensive web test cases

## Attachments
- Place screenshots under `docs/images/web/<TC-ID>/`
- Include screen recordings for critical flows (registration, 2FA, purge)

---

## Vue Pages Coverage (Web)

The following test cases cover all Vue pages in `frontend/src/pages`. Each case follows the standard template and includes atomic, verifiable steps. Use Chrome 120/macOS unless noted.

### Pages Index
- WEB-TC-010 — DoctorAppointment.vue
- WEB-TC-011 — DoctorDashboard.vue
- WEB-TC-012 — DoctorMessaging.vue
- WEB-TC-013 — DoctorPatientArchive.vue
- WEB-TC-014 — DoctorPatientManagement.vue
- WEB-TC-015 — DoctorSettings.vue
- WEB-TC-016 — ErrorNotFound.vue
- WEB-TC-017 — ForgotPasswordPage.vue
- WEB-TC-018 — IndexPage.vue
- WEB-TC-019 — LandingPage.vue
- WEB-TC-020 — NurseDashboard.vue
- WEB-TC-021 — NurseMedicineInventory.vue
- WEB-TC-022 — NurseMessaging.vue
- WEB-TC-023 — NursePatientArchive.vue
- WEB-TC-024 — NursePatientAssessment.vue
- WEB-TC-025 — NurseQueueManagement.vue
- WEB-TC-026 — NurseSettings.vue
- WEB-TC-027 — OtpVerifyPage.vue
- WEB-TC-028 — PatientAppointmentSchedule.vue
- WEB-TC-029 — PatientDashboard.vue
- WEB-TC-030 — PatientNotifications.vue
- WEB-TC-031 — PatientQueue.vue
- WEB-TC-032 — ResetPasswordPage.vue
- WEB-TC-033 — RoleSelectionPage.vue
- WEB-TC-034 — TermsAndConditions.vue
- WEB-TC-035 — VerificationPage.vue
- WEB-TC-036 — DoctorPredictiveAnalytics.vue
- WEB-TC-037 — LoginPage.vue
- WEB-TC-038 — NurseAnalytics.vue
- WEB-TC-039 — PatientSettings.vue
- WEB-TC-040 — RegisterPage.vue

---

## WEB-TC-010 — DoctorAppointment.vue
### Identification
- Test Case ID: WEB-TC-010
- Module: Web (Vue Page: DoctorAppointment)
- Priority: Medium
- Related Requirement: Appointment scheduling and management
### Details
- Description: Verify appointment creation, rescheduling, and cancellation.
- Pre-requisites: Logged-in doctor; patients exist.
- Post-requisites: Appointment records updated accordingly.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Navigate to Doctor Appointment page | Page loads with calendar/list |  | Chrome 120 |  |
| 2 | Create appointment for patient | Confirmation; record saved |  | Chrome 120 |  |
| 3 | Negative: overlapping time slot | Validation error shown |  | Chrome 120 |  |

## WEB-TC-011 — DoctorDashboard.vue
### Identification
- Test Case ID: WEB-TC-011
- Module: Web (Vue Page: DoctorDashboard)
- Priority: Medium
### Details
- Description: Verify KPIs/cards load and navigation links work.
- Pre-requisites: Authenticated doctor; data available.
- Post-requisites: None beyond display correctness.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Doctor Dashboard | KPIs/cards render |  | Chrome 120 |  |
| 2 | Click link to Messaging | Navigates to DoctorMessaging |  | Chrome 120 |  |
| 3 | Negative: API error | Graceful error message |  | Chrome 120 |  |

## WEB-TC-012 — DoctorMessaging.vue
### Identification
- Test Case ID: WEB-TC-012
- Module: Web (Vue Page: DoctorMessaging)
- Priority: Medium
### Details
- Description: Verify sending, receiving, and listing messages.
- Pre-requisites: Logged-in doctor; recipient available.
- Post-requisites: Message saved and visible to recipient.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Messaging page | Thread list visible |  | Chrome 120 |  |
| 2 | Send a message | Appears in thread |  | Chrome 120 |  |
| 3 | Negative: empty message | Validation error |  | Chrome 120 |  |

## WEB-TC-013 — DoctorPatientArchive.vue
### Identification
- Test Case ID: WEB-TC-013
- Module: Web (Vue Page: DoctorPatientArchive)
- Priority: Medium
### Details
- Description: Verify archive listing and detail view of assessments.
- Pre-requisites: Patient assessment archives exist.
- Post-requisites: None.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Archive page | List of archives |  | Chrome 120 |  |
| 2 | View archive detail | Encrypted data preview/decrypted summary |  | Chrome 120 |  |
| 3 | Negative: unauthorized access | 403 error |  | Chrome 120 |  |

## WEB-TC-014 — DoctorPatientManagement.vue
### Identification
- Test Case ID: WEB-TC-014
- Module: Web (Vue Page: DoctorPatientManagement)
- Priority: Medium
### Details
- Description: Verify patient listing, search, and profile open.
- Pre-requisites: Patients present.
- Post-requisites: None.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Patient Management | List renders |  | Chrome 120 |  |
| 2 | Search by name | Filtered results |  | Chrome 120 |  |
| 3 | Negative: invalid query | Graceful empty-state |  | Chrome 120 |  |

## WEB-TC-015 — DoctorSettings.vue
### Identification
- Test Case ID: WEB-TC-015
- Module: Web (Vue Page: DoctorSettings)
- Priority: Low
### Details
- Description: Verify settings update persists.
- Pre-requisites: Authenticated doctor.
- Post-requisites: Settings saved.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Settings | Form populated |  | Chrome 120 |  |
| 2 | Update preferences | 200 OK; toast confirmation |  | Chrome 120 |  |
| 3 | Negative: invalid value | Validation error |  | Chrome 120 |  |

## WEB-TC-016 — ErrorNotFound.vue
### Identification
- Test Case ID: WEB-TC-016
- Module: Web (Vue Page: ErrorNotFound)
- Priority: Low
### Details
- Description: Verify 404 page appears for unknown routes.
- Pre-requisites: None.
- Post-requisites: None.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Navigate to unknown route | 404 page visible |  | Chrome 120 |  |
| 2 | Click return home | Navigates to IndexPage |  | Chrome 120 |  |

## WEB-TC-017 — ForgotPasswordPage.vue
### Identification
- Test Case ID: WEB-TC-017
- Module: Web (Vue Page: ForgotPasswordPage)
- Priority: Medium
### Details
- Description: Verify password reset request and validations.
- Pre-requisites: Existing account.
- Post-requisites: Reset email queued.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Forgot Password | Form visible |  | Chrome 120 |  |
| 2 | Submit registered email | Success message |  | Chrome 120 |  |
| 3 | Negative: unknown email | Error/neutral feedback |  | Chrome 120 |  |

## WEB-TC-018 — IndexPage.vue
### Identification
- Test Case ID: WEB-TC-018
- Module: Web (Vue Page: IndexPage)
- Priority: Low
### Details
- Description: Verify default route content.
- Pre-requisites: None.
- Post-requisites: None.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open root route | Index content loads |  | Chrome 120 |  |
| 2 | Navigate to Login | Login page visible |  | Chrome 120 |  |

## WEB-TC-019 — LandingPage.vue
### Identification
- Test Case ID: WEB-TC-019
- Module: Web (Vue Page: LandingPage)
- Priority: Low
### Details
- Description: Verify hero section, CTA buttons, and navigation.
- Pre-requisites: None.
- Post-requisites: None.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open landing | Hero and CTA visible |  | Chrome 120 |  |
| 2 | Click Register CTA | Navigates to RegisterPage |  | Chrome 120 |  |

## WEB-TC-020 — NurseDashboard.vue
### Identification
- Test Case ID: WEB-TC-020
- Module: Web (Vue Page: NurseDashboard)
- Priority: Medium
### Details
- Description: Verify KPIs/cards and links.
- Pre-requisites: Authenticated nurse.
- Post-requisites: None.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Nurse Dashboard | KPIs/cards render |  | Chrome 120 |  |
| 2 | Navigate to Queue | NurseQueueManagement opens |  | Chrome 120 |  |

## WEB-TC-021 — NurseMedicineInventory.vue
### Identification
- Test Case ID: WEB-TC-021
- Module: Web (Vue Page: NurseMedicineInventory)
- Priority: Medium
### Details
- Description: Verify listing, add/update inventory items.
- Pre-requisites: Nurse role.
- Post-requisites: Inventory updates persisted.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Inventory page | Items listed |  | Chrome 120 |  |
| 2 | Add new item | Item appears |  | Chrome 120 |  |
| 3 | Negative: invalid quantity | Validation error |  | Chrome 120 |  |

## WEB-TC-022 — NurseMessaging.vue
### Identification
- Test Case ID: WEB-TC-022
- Module: Web (Vue Page: NurseMessaging)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Messaging | Threads visible |  | Chrome 120 |  |
| 2 | Send message | Appears in thread |  | Chrome 120 |  |

## WEB-TC-023 — NursePatientArchive.vue
### Identification
- Test Case ID: WEB-TC-023
- Module: Web (Vue Page: NursePatientArchive)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open archive | List visible |  | Chrome 120 |  |
| 2 | Open detail | Summary shown |  | Chrome 120 |  |

## WEB-TC-024 — NursePatientAssessment.vue
### Identification
- Test Case ID: WEB-TC-024
- Module: Web (Vue Page: NursePatientAssessment)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Fill assessment form | Validation passes |  | Chrome 120 |  |
| 2 | Submit | 201 Created |  | Chrome 120 |  |
| 3 | Negative: required field missing | Error shown |  | Chrome 120 |  |

## WEB-TC-025 — NurseQueueManagement.vue
### Identification
- Test Case ID: WEB-TC-025
- Module: Web (Vue Page: NurseQueueManagement)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Add patient to queue | Positions update |  | Chrome 120 |  |
| 2 | Serve first patient | Queue reorders |  | Chrome 120 |  |

## WEB-TC-026 — NurseSettings.vue
### Identification
- Test Case ID: WEB-TC-026
- Module: Web (Vue Page: NurseSettings)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open settings | Form populated |  | Chrome 120 |  |
| 2 | Save changes | 200 OK; toast |  | Chrome 120 |  |

## WEB-TC-027 — OtpVerifyPage.vue
### Identification
- Test Case ID: WEB-TC-027
- Module: Web (Vue Page: OtpVerify)
- Priority: High
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open OTP page | Prompt visible |  | Chrome 120 |  |
| 2 | Enter valid OTP | Verified; proceed |  | Chrome 120 |  |
| 3 | Negative: invalid/expired | Error shown |  | Chrome 120 |  |

## WEB-TC-028 — PatientAppointmentSchedule.vue
### Identification
- Test Case ID: WEB-TC-028
- Module: Web (Vue Page: PatientAppointmentSchedule)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open schedule | Calendar/form visible |  | Chrome 120 |  |
| 2 | Book appointment | Confirmation |  | Chrome 120 |  |

## WEB-TC-029 — PatientDashboard.vue
### Identification
- Test Case ID: WEB-TC-029
- Module: Web (Vue Page: PatientDashboard)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open dashboard | Widgets visible |  | Chrome 120 |  |
| 2 | Navigate to Notifications | Notifications page opens |  | Chrome 120 |  |

## WEB-TC-030 — PatientNotifications.vue
### Identification
- Test Case ID: WEB-TC-030
- Module: Web (Vue Page: PatientNotifications)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open notifications | List renders |  | Chrome 120 |  |
| 2 | Mark read | Status updates |  | Chrome 120 |  |

## WEB-TC-031 — PatientQueue.vue
### Identification
- Test Case ID: WEB-TC-031
- Module: Web (Vue Page: PatientQueue)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open queue | Position shown |  | Chrome 120 |  |
| 2 | Refresh | Updated position |  | Chrome 120 |  |

## WEB-TC-032 — ResetPasswordPage.vue
### Identification
- Test Case ID: WEB-TC-032
- Module: Web (Vue Page: ResetPassword)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open reset link | Reset form visible |  | Chrome 120 |  |
| 2 | Submit new password | Success; login prompt |  | Chrome 120 |  |

## WEB-TC-033 — RoleSelectionPage.vue
### Identification
- Test Case ID: WEB-TC-033
- Module: Web (Vue Page: RoleSelection)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open role selection | Roles listed |  | Chrome 120 |  |
| 2 | Choose role | Navigates to role flow |  | Chrome 120 |  |

## WEB-TC-034 — TermsAndConditions.vue
### Identification
- Test Case ID: WEB-TC-034
- Module: Web (Vue Page: TermsAndConditions)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Terms page | Content displays |  | Chrome 120 |  |
| 2 | Scroll and accept | Acceptance recorded |  | Chrome 120 |  |

## WEB-TC-035 — VerificationPage.vue
### Identification
- Test Case ID: WEB-TC-035
- Module: Web (Vue Page: Verification)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open verification | Form/prompt visible |  | Chrome 120 |  |
| 2 | Submit verification data | Success; proceed |  | Chrome 120 |  |

## WEB-TC-036 — DoctorPredictiveAnalytics.vue
### Identification
- Test Case ID: WEB-TC-036
- Module: Web (Vue Page: DoctorPredictiveAnalytics)
- Priority: Medium
### Details
- Description: Verify analytics cards/charts render and PDF generation works.
- Pre-requisites: Authenticated doctor; analytics data available.
- Post-requisites: Optional PDF report downloaded successfully.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Doctor Predictive Analytics | Charts/cards render |  | Chrome 120 |  |
| 2 | Click Generate PDF | Blob received; download starts |  | Chrome 120 |  |
| 3 | Negative: unauthenticated | 401 from endpoint |  | Chrome 120 |  |

## WEB-TC-037 — LoginPage.vue
### Identification
- Test Case ID: WEB-TC-037
- Module: Web (Vue Page: LoginPage)
- Priority: High
### Details
- Description: Verify login form validations and successful authentication for non-2FA users.
- Pre-requisites: Patient account active; backend reachable.
- Post-requisites: Tokens stored; navigation to dashboard allowed.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Login page | Form visible |  | Chrome 120 |  |
| 2 | Submit valid credentials | 200 OK; redirect to dashboard |  | Chrome 120 |  |
| 3 | Negative: invalid credentials | 401 Unauthorized; error banner |  | Chrome 120 |  |

## WEB-TC-038 — NurseAnalytics.vue
### Identification
- Test Case ID: WEB-TC-038
- Module: Web (Vue Page: NurseAnalytics)
- Priority: Medium
### Details
- Description: Verify nurse analytics charts render; cached data used when applicable.
- Pre-requisites: Authenticated nurse; analytics data available or cache primed.
- Post-requisites: None.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Nurse Analytics | Charts/cards render |  | Chrome 120 |  |
| 2 | Refresh analytics | Data updates |  | Chrome 120 |  |
| 3 | Negative: offline | Graceful message/cached data |  | Chrome 120 |  |

## WEB-TC-039 — PatientSettings.vue
### Identification
- Test Case ID: WEB-TC-039
- Module: Web (Vue Page: PatientSettings)
- Priority: Low
### Details
- Description: Verify patient settings form loads and persists changes.
- Pre-requisites: Authenticated patient.
- Post-requisites: Settings updated and persisted.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Patient Settings | Form populated |  | Chrome 120 |  |
| 2 | Save changes | 200 OK; toast confirmation |  | Chrome 120 |  |
| 3 | Negative: invalid value | Validation error shown |  | Chrome 120 |  |

## WEB-TC-040 — RegisterPage.vue
### Identification
- Test Case ID: WEB-TC-040
- Module: Web (Vue Page: RegisterPage)
- Priority: High
### Details
- Description: Verify role selection and registration form validations; successful account creation flow.
- Pre-requisites: Backend running; email backend configured.
- Post-requisites: New account exists; redirected to login or verification.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Register page | Role options + form visible |  | Chrome 120 |  |
| 2 | Submit valid details | 201 Created; success message |  | Chrome 120 |  |
| 3 | Negative: missing required fields | Validation errors |  | Chrome 120 |  |