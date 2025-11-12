# Queue & Appointment System Pseudocode

This document outlines pseudocode-level functions and process descriptions for creating and managing queue schedules, patient queues, patient dashboards, patient appointment scheduling, doctor appointments, and doctor dashboards. It is grounded by current structures and endpoints observed in the codebase.

## Legend
- `api.get|post|put|delete(path, payload?)` — HTTP calls to backend.
- `ws = new WebSocket(url)` — WebSocket connection.
- `store.*` — Vue Pinia stores and helpers.
- `notify(type, message)` — UX notifications.
- `schedule` — Queue schedule entity (department, start/end, days, is_active, override).
- `queueStatus` — Live queue status entity (is_open, current_serving, total_waiting, estimate).

---

## Queue Schedule (Nurse-side)

### Create/Update Schedule
```
function upsertQueueSchedule(input):
  # input: { department, start_time, end_time, days_of_week[], is_active, manual_override, override_status }
  validate input fields
  if input.id exists:
    response = api.put('/operations/queue/schedules/{id}/', input)
  else:
    response = api.post('/operations/queue/schedules/', input)
  notify('positive', 'Queue schedule saved')
  refreshSchedulesAndStatus()
```

### Load Schedules + Merge Actual Status
```
function refreshSchedulesAndStatus():
  schedules = api.get('/operations/queue/schedules/')
  statuses  = api.get('/operations/queue/status/')
  for s in schedules:
    s.is_open = (statuses.find(x => x.department == s.department)?.is_open) or false
  currentSchedule = pickByDepartmentOrDefault(schedules, form.department)
```

### Manual Override (Open/Close)
```
function setManualOverride(department, enable):
  api.post('/operations/queue/status/toggle/', { department, is_open: enable })
  logStatusChange('manual', department, enable)
  notify('info', enable ? 'Queue opened' : 'Queue closed')
  refreshSchedulesAndStatus()
```

### Auto-Open/Close (Cron/Celery)
```
function autoApplySchedules(now):
  schedules = loadActiveSchedules()
  for each schedule in schedules:
    if schedule.manual_override == true:
      continue
    if isDayEnabled(now, schedule.days_of_week):
      if withinTimeRange(now.time, schedule.start_time, schedule.end_time):
        ensureQueueOpen(schedule.department, reason='schedule')
      else:
        ensureQueueClosed(schedule.department, reason='schedule')
```

---

## Queue Management System (Core)

### Live Queue Status
```
function loadQueueStatus(department):
  return api.get('/operations/queue/status/', { params: { department } })

function updateQueueStatus(department, patch):
  response = api.put('/operations/queue/status/{department}/', patch)
  broadcastWS('queue_status_update', department)
  return response
```

### Patient Queue Lists
```
function loadQueuePatients():
  data = api.get('/operations/nurse/queue/patients/')
  return {
    normal: data.normal_queue,
    priority: data.priority_queue,
  }

function addPatientToQueue(patientId, department, priority=false):
  api.post('/operations/queue/add/', { patient_id: patientId, department, priority })
  notify('positive', 'Patient added to queue')
  broadcastWS('queue_status_update', department)

function advanceQueue(department):
  api.post('/operations/queue/advance/', { department })
  notify('info', 'Advanced to next queue number')
  broadcastWS('queue_status_update', department)
```

### WebSocket Refresh
```
function setupQueueWS(department):
  ws = new WebSocket(`ws://<host>/ws/queue/${department}/`)
  ws.onmessage = (event) => {
    payload = JSON.parse(event.data)
    if payload.type in ['queue_status','queue_status_update','queue_schedule','queue_schedule_update','queue_notification']:
      refreshSchedulesAndStatus()
      loadQueuePatients()
  }
```

---

## Patient Queue (Patient-facing)

### View My Queue Status
```
function loadPatientQueueSummary(department):
  summary = api.get('/operations/patient/dashboard/summary/', { params: { department } })
  # expected: { nowServing, myQueueStatus }
  return summary
```

### Join Queue from Patient App
```
function requestJoinQueue(patientId, department):
  # may be gated by appointment or eligibility rules
  res = api.post('/operations/queue/join/', { patient_id: patientId, department })
  notify('positive', 'You joined the queue')
  return res
```

### Leave/Cancel Queue
```
function leaveQueue(patientId, department):
  res = api.post('/operations/queue/leave/', { patient_id: patientId, department })
  notify('warning', 'You left the queue')
  return res
```

---

## Patient Dashboard

### Initialize Dashboard
```
function initPatientDashboard():
  summary = loadPatientQueueSummary('OPD')
  appointmentsStore.loadAppointments()
  initLucideIconsIfAvailable()
  renderNowServing(summary.nowServing)
  renderMyQueueStatus(summary.myQueueStatus)
```

### Open Next Appointment Modal
```
function openNextApptModal():
  next = appointmentsStore.nextAppointment
  if next:
    showModal('nextAppointmentDetails', next)
```

---

## Patient Appointment Schedule

### Book Appointment
```
function bookAppointment(form):
  # form: { type, department, date, time, doctor_id?, reason? }
  validate(form)
  # Normalize date/time formats (MM/DD/YYYY, HH:MM 24h)
  payload = normalizeForm(form)
  res = api.post('/operations/patient/appointments/', payload)
  appointmentsStore.append(res.data)
  notify('positive', 'Appointment booked')
  return res.data
```

### Filter Appointments by Tab + Search
```
function filterAppointments({ tab, query }):
  list = appointmentsStore.all
  filtered = byStatusTab(list, tab)  # scheduled|rescheduled|cancelled|completed
  if query:
    filtered = fullTextFilter(filtered, query)
  return filtered
```

### Reschedule/Cancel
```
function rescheduleAppointment(apptId, newDate, newTime):
  res = api.put(`/operations/patient/appointments/${apptId}/`, { date: newDate, time: newTime })
  appointmentsStore.update(apptId, res.data)
  notify('info', 'Appointment rescheduled')

function cancelAppointment(apptId, reason):
  res = api.post(`/operations/patient/appointments/${apptId}/cancel/`, { reason })
  appointmentsStore.update(apptId, res.data)
  notify('warning', 'Appointment cancelled')
```

---

## Doctor Appointment (Doctor-facing)

### Verify Availability & Accept
```
function acceptAppointment(apptId):
  availability = api.get('/operations/doctor/availability/')
  if not isAvailable(availability, apptId):
    notify('warning', 'Not available for requested time')
    return
  res = api.post(`/operations/doctor/appointments/${apptId}/accept/`)
  notify('positive', 'Appointment accepted')
  return res.data
```

### Update Consultation Status
```
function completeConsultation(apptId, notes):
  res = api.post(`/operations/doctor/appointments/${apptId}/complete/`, { notes })
  notify('positive', 'Consultation marked completed')
  return res.data
```

---

## Doctor Dashboard

### Load Doctor Dashboard Data
```
function loadDoctorDashboard():
  # patients, tasks, vitals, medications, queue
  patientsQueue = api.get('/operations/nurse/queue/patients/')
  myPatients    = api.get('/operations/doctor/patients/')
  todaysTasks   = summarizeTasks(myPatients)
  renderDashboard({ patientsQueue, myPatients, todaysTasks })
```

### Real-time Queue Updates
```
function setupDoctorQueueWS(department):
  ws = new WebSocket(`ws://<host>/ws/queue/${department}/`)
  ws.onmessage = (event) => {
    data = JSON.parse(event.data)
    if data.type == 'queue_status' or data.type == 'queue_status_update':
      refreshQueuePanels()
  }
```

---

## Data Models (observed)

### QueueStatus
- `department: 'OPD'|'Billing'|'Pharmacy'|'Appointment'`
- `is_open: boolean`
- `current_serving: number?`
- `total_waiting: number`
- `estimated_wait_time: duration?`
- `status_message: string`
- `last_updated_by: User?`
- `last_updated_at: datetime`

### QueueSchedule
- `department`
- `start_time`
- `end_time`
- `days_of_week: [0..6]`
- `is_active: boolean`
- `manual_override: boolean`
- `override_status: 'enabled'|'disabled'|'auto'`
- `nurse: NurseProfile`
- `timestamps`

### QueueManagement (patient-level queue entry)
- `patient: PatientProfile`
- `queue_number`
- `started_at: datetime?`
- `department`
- `priority?: boolean`

---

## UX Considerations
- Show clear status chips: `Active/Inactive`, `Open/Closed` per schedule.
- Provide department filter for schedules and queue lists.
- Use WebSocket to keep queue panels reactive without manual refresh.
- Validate date/time inputs and normalize formats before API.
- Provide human-readable labels for department and appointment type.

## Operational Notes
- Auto-close/open is handled via scheduled jobs (management command / Celery).
- Status changes should be logged (`QueueStatusLog`) with reason: `schedule|manual|system`.
- Frontend tabs segment appointment lists by status to simplify navigation.