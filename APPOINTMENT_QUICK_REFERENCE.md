# Appointment Management - Quick Reference Guide

## 🎯 Overview
The PatientAppointmentSchedule component now supports complete appointment lifecycle management with three main sections:
- **Scheduled Appointments** - Active upcoming appointments
- **Rescheduled Appointments** - Appointments that have been modified
- **Cancelled Appointments** - Historical record of cancelled appointments

---

## 🚀 Quick Start

### For Patients

#### Schedule New Appointment
1. Click **"BOOK NOW"** button
2. Fill in the form:
   - Appointment Type (e.g., General Consultation)
   - Department (e.g., Cardiology)
   - Select Doctor (optional - shows verified doctors only)
   - Date (MM/DD/YYYY format)
   - Time (24-hour format HH:MM)
   - Reason for appointment
3. Click **"Schedule Appointment"**
4. System will check for duplicates and confirm

#### Reschedule Appointment
1. Navigate to appointment card in any tab
2. Click **"Reschedule"** button
3. Form pre-fills with existing data
4. Update date/time as needed
5. Click **"Reschedule Appointment"**
6. Appointment moves to "RESCHEDULED" tab

#### Cancel Appointment
1. Click **"Cancel"** on appointment card
2. Review appointment details in confirmation modal
3. Optionally add cancellation reason
4. Choose action:
   - **"Keep Appointment"** - No changes
   - **"Reschedule Instead"** - Opens reschedule form
   - **"Confirm Cancellation"** - Cancels appointment
5. Appointment moves to "CANCELLED" tab

---

## 📋 Features

### ✅ Implemented Features

| Feature | Description | Status |
|---------|-------------|--------|
| **Schedule** | Book new appointments with verified doctors | ✅ |
| **Reschedule** | Modify date/time of existing appointments | ✅ |
| **Cancel** | Cancel appointments with optional reason | ✅ |
| **Duplicate Check** | Prevents booking same time slot twice | ✅ |
| **Status Tracking** | Automatic categorization by status | ✅ |
| **Search** | Filter by doctor, department, or type | ✅ |
| **Responsive UI** | Works on all devices | ✅ |
| **Real-time Updates** | Changes reflect immediately | ✅ |
| **Notifications** | Doctors notified of changes | ✅ |

### 🎨 UI Components

#### Appointment Cards
Each appointment displays:
- Doctor name and specialization
- Status badge (color-coded)
- Date and time
- Appointment type
- Reason/notes
- Action buttons

#### Color Coding
- 🟢 **Green Badge** - Scheduled
- 🟠 **Orange Badge** - Rescheduled  
- ⚫ **Grey Badge** - Cancelled

#### Tabs
- **UPCOMING** - Shows scheduled appointments
- **RESCHEDULED** - Shows modified appointments
- **CANCELLED** - Shows cancelled appointments

---

## 🔧 Developer Reference

### Frontend Files Modified
- `/frontend/src/pages/PatientAppointmentSchedule.vue`

### Backend Files Modified
- `/backend/operations/models.py` - Added status & reason fields
- `/backend/operations/views.py` - Added reschedule/cancel endpoints
- `/backend/operations/serializers.py` - Enhanced serializer
- `/backend/operations/urls.py` - Added new routes

### Database Migration
- `backend/operations/migrations/0010_add_reschedule_cancel_fields.py`

---

## 🔌 API Endpoints

### 1. Get Patient Appointments
```http
GET /operations/patient/appointments/
Authorization: Bearer {token}
```

**Response:**
```json
{
  "results": [
    {
      "appointment_id": 1,
      "patient_name": "John Doe",
      "doctor_name": "Dr. Smith",
      "doctor_id": 5,
      "department": "Cardiology",
      "appointment_date": "2025-10-20T10:00:00Z",
      "appointment_time": "10:00:00",
      "status": "scheduled",
      "type": "consultation",
      "cancellation_reason": null,
      "reschedule_reason": null
    }
  ]
}
```

### 2. Schedule Appointment
```http
POST /operations/appointments/schedule/
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "type": "general-consultation",
  "department": "cardiology",
  "date": "2025-10-20T00:00:00Z",
  "time": "10:00",
  "reason": "Regular checkup",
  "doctor_id": "5"
}
```

### 3. Reschedule Appointment
```http
PATCH /operations/appointments/{id}/reschedule/
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "date": "2025-10-22T00:00:00Z",
  "time": "14:00",
  "reschedule_reason": "Patient requested reschedule"
}
```

### 4. Cancel Appointment
```http
PATCH /operations/appointments/{id}/cancel/
Authorization: Bearer {token}
Content-Type: application/json
```

**Request:**
```json
{
  "cancellation_reason": "Unable to attend"
}
```

---

## 🧪 Testing

### Run Backend Test
```bash
cd /Users/judeibardaloza/Desktop/medisync
python test_appointment_management.py
```

### Manual Testing Checklist
- [ ] Schedule new appointment
- [ ] Verify in UPCOMING tab
- [ ] Reschedule appointment
- [ ] Verify in RESCHEDULED tab
- [ ] Try duplicate time (should warn)
- [ ] Cancel appointment
- [ ] Verify in CANCELLED tab
- [ ] Reschedule from cancel modal
- [ ] Test search functionality
- [ ] Test on mobile device

---

## ⚠️ Important Notes

### Date/Time Validation
- ✅ Dates must be in future
- ✅ Time format: 24-hour (HH:MM)
- ✅ Date format: MM/DD/YYYY
- ❌ Past dates are rejected

### Duplicate Prevention
- System checks date + time combination
- Excludes cancelled appointments
- Excludes appointment being rescheduled
- Shows clear warning message

### Status Flow
```
New Appointment → [scheduled]
                     ↓
           ┌─────────┴─────────┐
           ↓                   ↓
     [rescheduled]        [cancelled]
```

### Doctor Selection
- Only verified doctors shown
- Must have `verification_status = 'approved'`
- Must be active (`is_active = true`)
- Filtered by selected department

---

## 🐛 Troubleshooting

### Appointment not appearing?
1. Check if user is logged in as patient
2. Verify API endpoint returns data
3. Check browser console for errors
4. Refresh the page

### Can't reschedule?
1. Ensure appointment belongs to current user
2. Check new date/time is in future
3. Verify no duplicate exists at new time

### Duplicate warning keeps showing?
1. Check if another appointment exists at that time
2. Verify date/time format is correct
3. Ensure cancelled appointments are excluded

### Doctor list is empty?
1. Verify doctors are verified (`verification_status = 'approved'`)
2. Check doctors are active (`is_active = true`)
3. Ensure doctors have correct department/specialization
4. Check `available_for_consultation = true`

---

## 📱 Mobile Support

### Responsive Features
- ✅ Touch-friendly buttons
- ✅ Scrollable appointment cards
- ✅ Bottom navigation bar
- ✅ Collapsible forms
- ✅ Optimized for small screens

### Recommended Testing Devices
- iPhone (iOS Safari)
- Android (Chrome)
- iPad (tablet view)
- Various screen sizes (320px - 1920px)

---

## 🔐 Security

### Authentication
- All endpoints require JWT token
- User can only access own appointments
- Appointment ownership verified on backend

### Validation
- Input sanitization
- Date/time validation
- SQL injection prevention
- XSS protection

---

## 📚 Additional Resources

### Documentation Files
- `APPOINTMENT_MANAGEMENT_IMPLEMENTATION.md` - Detailed implementation guide
- `test_appointment_management.py` - Backend test script

### Component Location
- Frontend: `/frontend/src/pages/PatientAppointmentSchedule.vue`
- Backend Views: `/backend/operations/views.py`
- Backend Models: `/backend/operations/models.py`

---

## 💡 Tips & Best Practices

### For Patients
- 📅 Schedule appointments at least 24 hours in advance
- 🔔 Check notifications for appointment confirmations
- 📝 Provide detailed reasons for better doctor preparation
- ⏰ Arrive 10-15 minutes early for appointments

### For Developers
- 🧪 Always test on multiple devices
- 📊 Monitor API response times
- 🔍 Check error logs regularly
- 📱 Test offline behavior
- 🔄 Keep dependencies updated

---

## 🎓 Quick Commands

### Start Development Server
```bash
# Backend
cd /Users/judeibardaloza/Desktop/medisync
python manage.py runserver

# Frontend
cd /Users/judeibardaloza/Desktop/medisync/frontend
npm run dev
```

### Run Migrations
```bash
cd /Users/judeibardaloza/Desktop/medisync
python manage.py migrate
```

### Create Test Data
```bash
python manage.py shell
>>> from backend.analytics.management.commands.populate_dummy_data import Command
>>> Command().handle()
```

---

## 📞 Support

For issues or questions:
1. Check console logs (Frontend: Browser DevTools, Backend: Terminal)
2. Review error messages
3. Consult documentation files
4. Check API response in Network tab

---

**Last Updated:** October 13, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

