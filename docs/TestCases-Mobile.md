# MediSync Mobile Test Cases

- Version: 1.0.0
- Last Updated: 2025-11-11
- Module: Mobile (Capacitor iOS/Android)
- Scope: Test planning and execution record for mobile application

## Template (Use for every test case)

### 1) Test Case Identification
- Test Case ID: `MOBILE-TC-XXX`
- Module: `Mobile`
- Priority: `High | Medium | Low`
- Related Requirement: short reference to design requirement or user story

### 2) Test Case Details
- Description: concise statement of what is being validated
- Pre-requisites: list all conditions (e.g., app installed, test accounts, connectivity)
- Post-requisites: expected system state after completion

### 3) Test Execution Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results (Pass/Fail) |
|---|---|---|---|---|---|

Notes:
- Keep each step atomic and verifiable.
- Include both positive and negative steps where applicable.
- Add screenshots for critical steps in `docs/images/mobile/<TC-ID>/`.

---

## MOBILE-TC-001 — Login With Connectivity Pre-warm and Endpoint Optimization (iOS)

### Identification
- Test Case ID: MOBILE-TC-001
- Module: Mobile
- Priority: High
- Related Requirement: iOS pre-warm connection; `optimizeEndpoint` base URL selection

### Details
- Description: Validate mobile login sequence triggers pre-warm on iOS and selects working API base URL; confirm successful authentication.
- Pre-requisites: iOS device (iPhone 13, iOS 17); app installed; test user credentials; multiple candidate endpoints configured.
- Post-requisites: `access` token stored; chosen base URL persisted.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Launch app | Splash + login screen |  | iPhone 13 (iOS 17) |  |
| 2 | Wait for pre-warm | Silent connectivity test completes |  | iPhone 13 (iOS 17) |  |
| 3 | Enter valid credentials | 200 OK; dashboard visible |  | iPhone 13 (iOS 17) |  |
| 4 | Verify base URL selection | Working base URL stored in local storage |  | iPhone 13 (iOS 17) |  |
| 5 | Negative: all endpoints unreachable | Error banner; retry option; no crash |  | iPhone 13 (iOS 17) |  |

---

## MOBILE-TC-002 — Doctor Analytics PDF Generation and Device Save

### Identification
- Test Case ID: MOBILE-TC-002
- Module: Mobile
- Priority: Medium
- Related Requirement: PDF report generation from doctor analytics page

### Details
- Description: Validate PDF generation flow on mobile and confirm file saved with correct MIME type; preview/share options available.
- Pre-requisites: Logged-in doctor; storage permissions granted.
- Post-requisites: `doctor_analytics_report_<date>.pdf` present in app documents.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Navigate to Doctor Analytics | Page loads |  | Pixel 6 (Android 14) |  |
| 2 | Tap Generate PDF | Blob received; save prompt |  | Pixel 6 (Android 14) |  |
| 3 | Open preview | PDF renders |  | Pixel 6 (Android 14) |  |
| 4 | Negative: permission denied | Prompt to grant storage; operation aborted |  | Pixel 6 (Android 14) |  |

---

## MOBILE-TC-003 — Receive and Decrypt Secure Transmission

### Identification
- Test Case ID: MOBILE-TC-003
- Module: Mobile
- Priority: High
- Related Requirement: Secure transmissions and audits

### Details
- Description: Validate listing and detail retrieval of secure transmissions; confirm client-side decrypt works with stored private key.
- Pre-requisites: Doctor has registered public key; device holds matching private key; transmission exists.
- Post-requisites: Transmission status marked `received`; audit event logged; decrypted data shown.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open transmissions list | New item visible |  | iPhone 13 |  |
| 2 | Open transmission detail | Crypto fields present |  | iPhone 13 |  |
| 3 | Perform decrypt | Plaintext displayed; checksum verified |  | iPhone 13 |  |
| 4 | Negative: missing private key | Error; guidance to import key |  | iPhone 13 |  |

---

## MOBILE-TC-004 — 2FA Login Flow (Doctor/Nurse)

### Identification
- Test Case ID: MOBILE-TC-004
- Module: Mobile
- Priority: High
- Related Requirement: Email OTP verification on mobile

### Details
- Description: Validate OTP prompt during login and successful token issuance after correct OTP; confirm failure cases.
- Pre-requisites: Staff account with 2FA enabled; email reachable on device.
- Post-requisites: Tokens stored; navigation enabled.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Login with credentials | OTP prompt appears |  | Pixel 6 |  |
| 2 | Enter correct OTP | Tokens issued; dashboard visible |  | Pixel 6 |  |
| 3 | Negative: invalid OTP | Error message |  | Pixel 6 |  |
| 4 | Negative: expired OTP | Error message |  | Pixel 6 |  |

---

## MOBILE-TC-005 — Nurse Analytics Caching and Offline Behavior

### Identification
- Test Case ID: MOBILE-TC-005
- Module: Mobile
- Priority: Medium
- Related Requirement: Analytics caching and graceful offline handling

### Details
- Description: Validate analytics page loads cached data when offline; online refresh updates charts.
- Pre-requisites: Nurse account; analytics previously loaded online.
- Post-requisites: Charts render from cache offline; refresh updates on reconnect.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Load analytics online | Charts present |  | Pixel 6 |  |
| 2 | Toggle device offline | Offline indicator shown |  | Pixel 6 |  |
| 3 | Reopen analytics | Cached charts load |  | Pixel 6 |  |
| 4 | Go online and refresh | New data fetched |  | Pixel 6 |  |

---

## MOBILE-TC-006 — Robust Logout

### Identification
- Test Case ID: MOBILE-TC-006
- Module: Mobile
- Priority: Medium
- Related Requirement: Clear auth storage and navigate to login

### Details
- Description: Validate logout clears tokens and user storage, resets Axios auth header, and navigates to login.
- Pre-requisites: Logged-in user (any role).
- Post-requisites: No auth data in storage; app at login screen.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Tap Logout | Storage cleared; headers reset |  | iPhone 13 |  |
| 2 | Navigate back to app | Requires login |  | iPhone 13 |  |
| 3 | Negative: offline state | Logout still completes; local changes applied |  | iPhone 13 |  |

---

## MOBILE-TC-007 — Connectivity Fallback (Wi‑Fi vs Cellular)

### Identification
- Test Case ID: MOBILE-TC-007
- Module: Mobile
- Priority: Medium
- Related Requirement: Endpoint optimization and fallback

### Details
- Description: Validate connectivity tests select best base URL across Wi‑Fi and cellular; ensure persistence per network change.
- Pre-requisites: Multiple endpoints; ability to switch networks.
- Post-requisites: Base URL updated appropriately; stored in local storage.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Connect to Wi‑Fi and login | Working base URL selected |  | Pixel 6 |  |
| 2 | Switch to cellular | Optimization runs; base URL updated |  | Pixel 6 |  |
| 3 | Negative: DNS failure | Retry/backoff; user feedback; no crash |  | Pixel 6 |  |

---

## MOBILE-TC-008 — Push Notification for Secure Transmission

### Identification
- Test Case ID: MOBILE-TC-008
- Module: Mobile
- Priority: Low
- Related Requirement: Realtime updates (Channels/WebSocket or push)

### Details
- Description: Validate user receives notification when a new secure transmission arrives; tapping opens detail.
- Pre-requisites: Push notifications enabled or WebSocket consumer; transmission sent to doctor.
- Post-requisites: Notification logged; detail screen opens on tap.

### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Wait for new transmission | Notification received |  | iPhone 13 |  |
| 2 | Tap notification | App opens on transmission detail |  | iPhone 13 |  |
| 3 | Negative: notification disabled | No notification; manual refresh shows item |  | iPhone 13 |  |

---

## Version Control
- Document Version: 1.0.0
- Last Updated: 2025-11-11
- Change Log:
  - 1.0.0 — Initial comprehensive mobile test cases

## Attachments
- Place screenshots under `docs/images/mobile/<TC-ID>/`
- Include screen recordings for critical flows (login with optimization, secure transmission decrypt)

## Vue Pages Coverage (Mobile)

The following test cases cover all Vue pages in `frontend/src/pages` for mobile builds (Capacitor iOS/Android). Use iPhone 13 (iOS 17) and Pixel 6 (Android 14) as reference devices unless specified.

### Pages Index
- MOBILE-TC-020 — DoctorAppointment.vue
- MOBILE-TC-021 — DoctorDashboard.vue
- MOBILE-TC-022 — DoctorMessaging.vue
- MOBILE-TC-023 — DoctorPatientArchive.vue
- MOBILE-TC-024 — DoctorPatientManagement.vue
- MOBILE-TC-025 — DoctorPredictiveAnalytics.vue
- MOBILE-TC-026 — DoctorSettings.vue
- MOBILE-TC-027 — ErrorNotFound.vue
- MOBILE-TC-028 — ForgotPasswordPage.vue
- MOBILE-TC-029 — IndexPage.vue
- MOBILE-TC-030 — LandingPage.vue
- MOBILE-TC-031 — LoginPage.vue
- MOBILE-TC-032 — NurseAnalytics.vue
- MOBILE-TC-033 — NurseDashboard.vue
- MOBILE-TC-034 — NurseMedicineInventory.vue
- MOBILE-TC-035 — NurseMessaging.vue
- MOBILE-TC-036 — NursePatientArchive.vue
- MOBILE-TC-037 — NursePatientAssessment.vue
- MOBILE-TC-038 — NurseQueueManagement.vue
- MOBILE-TC-039 — NurseSettings.vue
- MOBILE-TC-040 — OtpVerifyPage.vue
- MOBILE-TC-041 — PatientAppointmentSchedule.vue
- MOBILE-TC-042 — PatientDashboard.vue
- MOBILE-TC-043 — PatientNotifications.vue
- MOBILE-TC-044 — PatientQueue.vue
- MOBILE-TC-045 — PatientSettings.vue
- MOBILE-TC-046 — RegisterPage.vue
- MOBILE-TC-047 — ResetPasswordPage.vue
- MOBILE-TC-048 — RoleSelectionPage.vue
- MOBILE-TC-049 — TermsAndConditions.vue
- MOBILE-TC-050 — VerificationPage.vue

---

## MOBILE-TC-020 — DoctorAppointment.vue
### Identification
- Test Case ID: MOBILE-TC-020
- Module: Mobile (Vue Page: DoctorAppointment)
- Priority: Medium
### Details
- Description: Verify appointment creation, rescheduling, and cancellation on mobile.
- Pre-requisites: Logged-in doctor; patients exist.
- Post-requisites: Appointment records updated.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Doctor Appointment | Calendar/list visible |  | Pixel 6 (Android 14) |  |
| 2 | Create appointment | Confirmation; record saved |  | Pixel 6 (Android 14) |  |
| 3 | Negative: overlapping slot | Validation error |  | Pixel 6 (Android 14) |  |

## MOBILE-TC-021 — DoctorDashboard.vue
### Identification
- Test Case ID: MOBILE-TC-021
- Module: Mobile (Vue Page: DoctorDashboard)
- Priority: Medium
### Details
- Description: Verify KPIs/cards and navigation works.
- Pre-requisites: Authenticated doctor.
- Post-requisites: None.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Doctor Dashboard | KPIs/cards render |  | iPhone 13 (iOS 17) |  |
| 2 | Tap Messaging | Navigates to DoctorMessaging |  | iPhone 13 (iOS 17) |  |

## MOBILE-TC-022 — DoctorMessaging.vue
### Identification
- Test Case ID: MOBILE-TC-022
- Module: Mobile (Vue Page: DoctorMessaging)
- Priority: Medium
### Details
- Description: Verify sending, receiving, and listing messages.
- Pre-requisites: Logged-in doctor; recipient available.
- Post-requisites: Message saved and visible.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Messaging | Thread list visible |  | Pixel 6 |  |
| 2 | Send message | Appears in thread |  | Pixel 6 |  |
| 3 | Negative: empty message | Validation error |  | Pixel 6 |  |

## MOBILE-TC-023 — DoctorPatientArchive.vue
### Identification
- Test Case ID: MOBILE-TC-023
- Module: Mobile (Vue Page: DoctorPatientArchive)
- Priority: Medium
### Details
- Description: Verify archive listing and detail view of assessments.
- Pre-requisites: Patient assessment archives exist.
- Post-requisites: None.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Archive | List of archives |  | iPhone 13 |  |
| 2 | Open archive detail | Encrypted data preview/decrypted summary |  | iPhone 13 |  |

## MOBILE-TC-024 — DoctorPatientManagement.vue
### Identification
- Test Case ID: MOBILE-TC-024
- Module: Mobile (Vue Page: DoctorPatientManagement)
- Priority: Medium
### Details
- Description: Verify patient listing, search, and profile open.
- Pre-requisites: Patients present.
- Post-requisites: None.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Patient Management | List renders |  | Pixel 6 |  |
| 2 | Search by name | Filtered results |  | Pixel 6 |  |

## MOBILE-TC-025 — DoctorPredictiveAnalytics.vue
### Identification
- Test Case ID: MOBILE-TC-025
- Module: Mobile (Vue Page: DoctorPredictiveAnalytics)
- Priority: Medium
### Details
- Description: Verify analytics cards/charts and mobile PDF generation.
- Pre-requisites: Authenticated doctor; storage permission granted.
- Post-requisites: Optional PDF saved.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Doctor Analytics | Charts/cards render |  | iPhone 13 |  |
| 2 | Tap Generate PDF | Blob received; save prompt |  | iPhone 13 |  |

## MOBILE-TC-026 — DoctorSettings.vue
### Identification
- Test Case ID: MOBILE-TC-026
- Module: Mobile (Vue Page: DoctorSettings)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Settings | Form populated |  | Pixel 6 |  |
| 2 | Save changes | 200 OK; toast |  | Pixel 6 |  |

## MOBILE-TC-027 — ErrorNotFound.vue
### Identification
- Test Case ID: MOBILE-TC-027
- Module: Mobile (Vue Page: ErrorNotFound)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Navigate to unknown route | 404 page visible |  | iPhone 13 |  |
| 2 | Tap return home | Navigates to IndexPage |  | iPhone 13 |  |

## MOBILE-TC-028 — ForgotPasswordPage.vue
### Identification
- Test Case ID: MOBILE-TC-028
- Module: Mobile (Vue Page: ForgotPasswordPage)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Forgot Password | Form visible |  | Pixel 6 |  |
| 2 | Submit registered email | Success message |  | Pixel 6 |  |

## MOBILE-TC-029 — IndexPage.vue
### Identification
- Test Case ID: MOBILE-TC-029
- Module: Mobile (Vue Page: IndexPage)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open root route | Index content loads |  | iPhone 13 |  |
| 2 | Navigate to Login | Login page visible |  | iPhone 13 |  |

## MOBILE-TC-030 — LandingPage.vue
### Identification
- Test Case ID: MOBILE-TC-030
- Module: Mobile (Vue Page: LandingPage)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open landing | Hero and CTA visible |  | Pixel 6 |  |
| 2 | Tap Register CTA | Navigates to RegisterPage |  | Pixel 6 |  |

## MOBILE-TC-031 — LoginPage.vue
### Identification
- Test Case ID: MOBILE-TC-031
- Module: Mobile (Vue Page: LoginPage)
- Priority: High
### Details
- Description: Validate login form validations and authentication for non-2FA users.
- Pre-requisites: Patient account active.
- Post-requisites: Tokens stored; navigation allowed.
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Login page | Form visible |  | iPhone 13 |  |
| 2 | Submit valid credentials | 200 OK; dashboard visible |  | iPhone 13 |  |
| 3 | Negative: invalid credentials | 401 Unauthorized |  | iPhone 13 |  |

## MOBILE-TC-032 — NurseAnalytics.vue
### Identification
- Test Case ID: MOBILE-TC-032
- Module: Mobile (Vue Page: NurseAnalytics)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Nurse Analytics | Charts/cards render |  | Pixel 6 |  |
| 2 | Refresh analytics | Data updates |  | Pixel 6 |  |

## MOBILE-TC-033 — NurseDashboard.vue
### Identification
- Test Case ID: MOBILE-TC-033
- Module: Mobile (Vue Page: NurseDashboard)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Nurse Dashboard | KPIs/cards render |  | iPhone 13 |  |
| 2 | Navigate to Queue | NurseQueueManagement opens |  | iPhone 13 |  |

## MOBILE-TC-034 — NurseMedicineInventory.vue
### Identification
- Test Case ID: MOBILE-TC-034
- Module: Mobile (Vue Page: NurseMedicineInventory)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Inventory | Items listed |  | Pixel 6 |  |
| 2 | Add new item | Item appears |  | Pixel 6 |  |

## MOBILE-TC-035 — NurseMessaging.vue
### Identification
- Test Case ID: MOBILE-TC-035
- Module: Mobile (Vue Page: NurseMessaging)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Messaging | Threads visible |  | iPhone 13 |  |
| 2 | Send message | Appears in thread |  | iPhone 13 |  |

## MOBILE-TC-036 — NursePatientArchive.vue
### Identification
- Test Case ID: MOBILE-TC-036
- Module: Mobile (Vue Page: NursePatientArchive)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open archive | List visible |  | Pixel 6 |  |
| 2 | Open detail | Summary shown |  | Pixel 6 |  |

## MOBILE-TC-037 — NursePatientAssessment.vue
### Identification
- Test Case ID: MOBILE-TC-037
- Module: Mobile (Vue Page: NursePatientAssessment)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Fill assessment form | Validation passes |  | iPhone 13 |  |
| 2 | Submit | 201 Created |  | iPhone 13 |  |

## MOBILE-TC-038 — NurseQueueManagement.vue
### Identification
- Test Case ID: MOBILE-TC-038
- Module: Mobile (Vue Page: NurseQueueManagement)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Add patient to queue | Positions update |  | Pixel 6 |  |
| 2 | Serve first patient | Queue reorders |  | Pixel 6 |  |

## MOBILE-TC-039 — NurseSettings.vue
### Identification
- Test Case ID: MOBILE-TC-039
- Module: Mobile (Vue Page: NurseSettings)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open settings | Form populated |  | iPhone 13 |  |
| 2 | Save changes | 200 OK; toast |  | iPhone 13 |  |

## MOBILE-TC-040 — OtpVerifyPage.vue
### Identification
- Test Case ID: MOBILE-TC-040
- Module: Mobile (Vue Page: OtpVerify)
- Priority: High
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open OTP page | Prompt visible |  | Pixel 6 |  |
| 2 | Enter valid OTP | Verified; proceed |  | Pixel 6 |  |
| 3 | Negative: invalid/expired | Error shown |  | Pixel 6 |  |

## MOBILE-TC-041 — PatientAppointmentSchedule.vue
### Identification
- Test Case ID: MOBILE-TC-041
- Module: Mobile (Vue Page: PatientAppointmentSchedule)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open schedule | Calendar/form visible |  | iPhone 13 |  |
| 2 | Book appointment | Confirmation |  | iPhone 13 |  |

## MOBILE-TC-042 — PatientDashboard.vue
### Identification
- Test Case ID: MOBILE-TC-042
- Module: Mobile (Vue Page: PatientDashboard)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open dashboard | Widgets visible |  | Pixel 6 |  |
| 2 | Navigate to Notifications | Notifications page opens |  | Pixel 6 |  |

## MOBILE-TC-043 — PatientNotifications.vue
### Identification
- Test Case ID: MOBILE-TC-043
- Module: Mobile (Vue Page: PatientNotifications)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open notifications | List renders |  | iPhone 13 |  |
| 2 | Mark read | Status updates |  | iPhone 13 |  |

## MOBILE-TC-044 — PatientQueue.vue
### Identification
- Test Case ID: MOBILE-TC-044
- Module: Mobile (Vue Page: PatientQueue)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open queue | Position shown |  | Pixel 6 |  |
| 2 | Pull to refresh | Updated position |  | Pixel 6 |  |

## MOBILE-TC-045 — PatientSettings.vue
### Identification
- Test Case ID: MOBILE-TC-045
- Module: Mobile (Vue Page: PatientSettings)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Patient Settings | Form populated |  | iPhone 13 |  |
| 2 | Save changes | 200 OK; toast |  | iPhone 13 |  |

## MOBILE-TC-046 — RegisterPage.vue
### Identification
- Test Case ID: MOBILE-TC-046
- Module: Mobile (Vue Page: RegisterPage)
- Priority: High
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Register page | Role options + form visible |  | Pixel 6 |  |
| 2 | Submit valid details | 201 Created; success message |  | Pixel 6 |  |
| 3 | Negative: missing fields | Validation errors |  | Pixel 6 |  |

## MOBILE-TC-047 — ResetPasswordPage.vue
### Identification
- Test Case ID: MOBILE-TC-047
- Module: Mobile (Vue Page: ResetPassword)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open reset link | Reset form visible |  | iPhone 13 |  |
| 2 | Submit new password | Success; login prompt |  | iPhone 13 |  |

## MOBILE-TC-048 — RoleSelectionPage.vue
### Identification
- Test Case ID: MOBILE-TC-048
- Module: Mobile (Vue Page: RoleSelection)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open role selection | Roles listed |  | Pixel 6 |  |
| 2 | Choose role | Navigates to role flow |  | Pixel 6 |  |

## MOBILE-TC-049 — TermsAndConditions.vue
### Identification
- Test Case ID: MOBILE-TC-049
- Module: Mobile (Vue Page: TermsAndConditions)
- Priority: Low
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open Terms page | Content displays |  | iPhone 13 |  |
| 2 | Scroll and accept | Acceptance recorded |  | iPhone 13 |  |

## MOBILE-TC-050 — VerificationPage.vue
### Identification
- Test Case ID: MOBILE-TC-050
- Module: Mobile (Vue Page: Verification)
- Priority: Medium
### Steps
| S.No | Action | Expected Output | Actual Output | Test Browser/Device | Results |
|---|---|---|---|---|---|
| 1 | Open verification | Form/prompt visible |  | Pixel 6 |  |
| 2 | Submit verification data | Success; proceed |  | Pixel 6 |  |