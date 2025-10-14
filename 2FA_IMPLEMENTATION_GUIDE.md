# Two-Factor Authentication (2FA) Implementation Guide

## Overview

This implementation adds Two-Factor Authentication (2FA) support for **doctors and nurses only** in the MediSync application. The implementation uses Time-based One-Time Passwords (TOTP) compatible with popular authenticator apps like Google Authenticator, Authy, Microsoft Authenticator, etc.

## Features

✅ **Enable 2FA** - Doctors and nurses can enable 2FA for their accounts
✅ **QR Code Generation** - Easy setup via QR code scanning or manual secret entry
✅ **Login Protection** - Requires OTP verification during login when 2FA is enabled
✅ **Disable 2FA** - Users can disable 2FA with password verification
✅ **Role-Based** - Only doctors and nurses can use 2FA (patients are restricted)

## Database Changes

Two new fields have been added to the `User` model:

```python
two_factor_enabled = models.BooleanField(default=False)
two_factor_secret = models.CharField(max_length=32, blank=True, null=True)
```

**Migration:** `backend/users/migrations/0010_user_two_factor_enabled_user_two_factor_secret.py`

## API Endpoints

### 1. Enable 2FA
**POST** `/api/users/2fa/enable/`

**Authentication:** Required (Bearer Token)

**Permissions:** Doctors and Nurses only

**Request Body:** None

**Response (Success - 200):**
```json
{
  "message": "Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)",
  "qr_code": "data:image/png;base64,...",
  "secret": "JBSWY3DPEHPK3PXP",
  "next_step": "Enter the 6-digit code from your authenticator app to verify and activate 2FA"
}
```

**Response (Error - 403):**
```json
{
  "error": "Two-factor authentication is only available for doctors and nurses."
}
```

### 2. Verify and Activate 2FA
**POST** `/api/users/2fa/verify/`

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "otp_code": "123456"
}
```

**Response (Success - 200):**
```json
{
  "message": "Two-factor authentication has been successfully enabled for your account.",
  "user": {
    "id": 1,
    "email": "doctor@example.com",
    "full_name": "Dr. John Doe",
    "role": "doctor",
    "two_factor_enabled": true,
    ...
  }
}
```

**Response (Error - 400):**
```json
{
  "error": "Invalid authentication code. Please try again."
}
```

### 3. Login (Modified)
**POST** `/api/users/login/`

**Authentication:** None

**Request Body:**
```json
{
  "email": "doctor@example.com",
  "password": "SecurePass123"
}
```

**Response (2FA Enabled - 200):**
```json
{
  "requires_2fa": true,
  "email": "doctor@example.com",
  "message": "Please enter your 6-digit authentication code."
}
```

**Response (2FA Not Enabled - 200):**
```json
{
  "message": "Login successful",
  "user": { ... },
  "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

### 4. Verify 2FA During Login
**POST** `/api/users/2fa/login/verify/`

**Authentication:** None

**Request Body:**
```json
{
  "email": "doctor@example.com",
  "otp_code": "123456"
}
```

**Response (Success - 200):**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "email": "doctor@example.com",
    "full_name": "Dr. John Doe",
    "role": "doctor",
    "two_factor_enabled": true,
    ...
  },
  "access": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

**Response (Error - 400):**
```json
{
  "error": "Invalid authentication code. Please try again."
}
```

### 5. Disable 2FA
**POST** `/api/users/2fa/disable/`

**Authentication:** Required (Bearer Token)

**Request Body:**
```json
{
  "password": "SecurePass123"
}
```

**Response (Success - 200):**
```json
{
  "message": "Two-factor authentication has been successfully disabled for your account.",
  "user": {
    "id": 1,
    "email": "doctor@example.com",
    "two_factor_enabled": false,
    ...
  }
}
```

**Response (Error - 400):**
```json
{
  "error": "Invalid password. Please try again."
}
```

## Setup Instructions

### 1. Install Dependencies

The required packages are already in `requirements.txt`:
```
pyotp==2.9.0
qrcode==7.4.2
```

Install them:
```bash
pip install -r requirements.txt
```

### 2. Run Migrations

The migration file has been created. Apply it:
```bash
python manage.py migrate
```

### 3. Test the Implementation

Run the comprehensive test script:
```bash
python test_2fa_implementation.py
```

## User Flow

### Enabling 2FA

1. **User logs in** with email and password
2. **User navigates to settings** and clicks "Enable 2FA"
3. **Frontend calls** `POST /api/users/2fa/enable/`
4. **Backend generates** a secret key and QR code
5. **Frontend displays** the QR code to the user
6. **User scans** QR code with authenticator app
7. **User enters** the 6-digit OTP code
8. **Frontend calls** `POST /api/users/2fa/verify/` with the OTP
9. **Backend verifies** OTP and activates 2FA
10. **2FA is now enabled** for the user

### Login with 2FA

1. **User enters** email and password
2. **Frontend calls** `POST /api/users/login/`
3. **Backend checks** if 2FA is enabled
   - If **not enabled**: returns access tokens immediately
   - If **enabled**: returns `{ requires_2fa: true }`
4. **Frontend shows** OTP input field
5. **User enters** 6-digit OTP code
6. **Frontend calls** `POST /api/users/2fa/login/verify/` with email and OTP
7. **Backend verifies** OTP and returns access tokens
8. **User is logged in**

### Disabling 2FA

1. **User navigates to settings**
2. **User clicks** "Disable 2FA"
3. **Frontend prompts** for password confirmation
4. **Frontend calls** `POST /api/users/2fa/disable/` with password
5. **Backend verifies** password and disables 2FA
6. **2FA is disabled** for the user

## Security Features

🔒 **Password Verification** - Disabling 2FA requires password confirmation
🔒 **Role-Based Access** - Only doctors and nurses can enable 2FA
🔒 **Time-Window Validation** - OTP codes are valid for a limited time window
🔒 **Secret Protection** - 2FA secrets are never exposed after initial setup
🔒 **Token-Based Authentication** - Uses JWT tokens for API authentication

## Frontend Integration

### Example: Enable 2FA

```javascript
// Enable 2FA
async function enable2FA() {
  const response = await axios.post('/api/users/2fa/enable/', {}, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  
  if (response.status === 200) {
    // Display QR code
    const qrCode = response.data.qr_code;
    const secret = response.data.secret;
    
    // Show QR code in modal
    showQRCodeModal(qrCode, secret);
  }
}

// Verify OTP
async function verify2FA(otpCode) {
  const response = await axios.post('/api/users/2fa/verify/', {
    otp_code: otpCode
  }, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  
  if (response.status === 200) {
    alert('2FA enabled successfully!');
  }
}
```

### Example: Login with 2FA

```javascript
// Step 1: Login
async function login(email, password) {
  const response = await axios.post('/api/users/login/', {
    email,
    password
  });
  
  if (response.data.requires_2fa) {
    // Show OTP input
    show2FAInput(email);
  } else {
    // Login successful, save tokens
    saveTokens(response.data.access, response.data.refresh);
  }
}

// Step 2: Verify OTP
async function verify2FALogin(email, otpCode) {
  const response = await axios.post('/api/users/2fa/login/verify/', {
    email,
    otp_code: otpCode
  });
  
  if (response.status === 200) {
    // Login successful, save tokens
    saveTokens(response.data.access, response.data.refresh);
  }
}
```

### Example: Disable 2FA

```javascript
async function disable2FA(password) {
  const response = await axios.post('/api/users/2fa/disable/', {
    password
  }, {
    headers: { Authorization: `Bearer ${accessToken}` }
  });
  
  if (response.status === 200) {
    alert('2FA disabled successfully!');
  }
}
```

## Testing with Authenticator Apps

### Recommended Apps

- **Google Authenticator** - iOS, Android
- **Authy** - iOS, Android, Desktop
- **Microsoft Authenticator** - iOS, Android
- **1Password** - iOS, Android, Desktop (requires subscription)

### Manual Entry

If QR code scanning doesn't work, users can manually enter:
- **Account**: user's email
- **Key**: the secret provided
- **Type**: Time-based

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200 OK** - Request successful
- **400 Bad Request** - Invalid input or OTP code
- **401 Unauthorized** - Invalid credentials or expired token
- **403 Forbidden** - User doesn't have permission (e.g., patient trying to enable 2FA)

## Troubleshooting

### OTP Code Not Working

1. **Check time sync** - TOTP requires accurate device time
2. **Try valid_window** - The implementation allows ±30 seconds
3. **Re-generate secret** - User can disable and re-enable 2FA

### QR Code Not Displaying

1. **Check response format** - Should be base64-encoded PNG
2. **Verify image tag** - Use `<img src="data:image/png;base64,..." />`
3. **Try manual entry** - Provide the secret key for manual setup

### Login Issues

1. **Verify 2FA status** - Check `user.two_factor_enabled` in database
2. **Test OTP generation** - Use `pyotp.TOTP(secret).now()` to generate test code
3. **Check secret** - Ensure `user.two_factor_secret` is not null

## Implementation Files

- **Models**: `backend/users/models.py` (lines 59-61)
- **Views**: `backend/users/views.py` (lines 549-747)
- **Serializers**: `backend/users/serializers.py` (lines 213-265)
- **URLs**: `backend/users/urls.py` (lines 25-29)
- **Test Script**: `test_2fa_implementation.py`

## Future Enhancements

- 📱 **SMS Backup Codes** - Backup verification via SMS
- 🔑 **Recovery Codes** - Generate one-time recovery codes
- 📊 **2FA Statistics** - Track 2FA adoption rate
- 📧 **Email Notifications** - Notify users when 2FA is enabled/disabled
- 🔄 **Backup Methods** - Multiple 2FA methods per user

## Support

For issues or questions, please contact the development team or create an issue in the project repository.

---

**Last Updated:** October 13, 2025
**Version:** 1.0.0

