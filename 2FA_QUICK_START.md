# 2FA Quick Start Guide

## 🚀 Quick Setup (3 minutes)

### 1. Run the Setup Script
```bash
./setup_2fa.sh
```

This will:
- Install `pyotp` and `qrcode` packages
- Apply database migrations
- Verify the installation

### 2. Start the Server
```bash
python manage.py runserver
```

### 3. Test the Implementation
```bash
python test_2fa_implementation.py
```

## 📱 Using 2FA

### For Doctors and Nurses:

1. **Login** to your account
2. **Go to Settings** (wherever you implement it in frontend)
3. **Click "Enable 2FA"**
4. **Scan QR code** with Google Authenticator or similar app
5. **Enter the 6-digit code** to verify
6. **Done!** 2FA is now active

### Next Login:

1. **Enter email and password** as usual
2. **Enter 6-digit code** from your authenticator app
3. **You're in!**

## 🔌 API Endpoints

### Enable 2FA
```bash
POST /api/users/2fa/enable/
Headers: Authorization: Bearer {token}
```

### Verify OTP to Activate 2FA
```bash
POST /api/users/2fa/verify/
Headers: Authorization: Bearer {token}
Body: { "otp_code": "123456" }
```

### Login (returns requires_2fa if enabled)
```bash
POST /api/users/login/
Body: { "email": "...", "password": "..." }
```

### Verify OTP During Login
```bash
POST /api/users/2fa/login/verify/
Body: { "email": "...", "otp_code": "123456" }
```

### Disable 2FA
```bash
POST /api/users/2fa/disable/
Headers: Authorization: Bearer {token}
Body: { "password": "..." }
```

## ✅ What Works

- ✅ Doctors can enable/disable 2FA
- ✅ Nurses can enable/disable 2FA
- ✅ Patients CANNOT enable 2FA (403 Forbidden)
- ✅ QR code generation for easy setup
- ✅ Login requires OTP when 2FA is enabled
- ✅ Password required to disable 2FA

## 📦 What Was Implemented

### Backend Changes:
1. **Models** - Added `two_factor_enabled` and `two_factor_secret` fields to User model
2. **Serializers** - Added 4 new serializers for 2FA operations
3. **Views** - Added 4 new endpoints + modified login endpoint
4. **URLs** - Added 4 new routes under `/api/users/2fa/`

### Files Modified:
- `backend/users/models.py`
- `backend/users/views.py`
- `backend/users/serializers.py`
- `backend/users/urls.py`

### Files Created:
- `backend/users/migrations/0010_user_two_factor_enabled_user_two_factor_secret.py`
- `test_2fa_implementation.py`
- `2FA_IMPLEMENTATION_GUIDE.md`
- `setup_2fa.sh`

## 🧪 Testing

Run the comprehensive test:
```bash
python test_2fa_implementation.py
```

Choose from:
1. Full 2FA flow for doctor
2. 2FA for nurse
3. 2FA restriction for patient
4. All tests

The test will:
- Register test users
- Enable 2FA
- Generate QR code
- Verify OTP
- Test login with 2FA
- Disable 2FA

## 📱 Authenticator Apps

Download any of these apps:
- **Google Authenticator** - Simple and reliable
- **Authy** - Has cloud backup and multi-device sync
- **Microsoft Authenticator** - Works well with Microsoft accounts
- **1Password** - If you use 1Password for passwords

## 🆘 Troubleshooting

**Q: OTP code not working?**
- Check your device time is correct (TOTP requires accurate time)
- Try the next code (codes change every 30 seconds)

**Q: Can't scan QR code?**
- Use manual entry instead
- Enter the secret key shown below the QR code

**Q: Lost access to authenticator app?**
- Contact admin or use password reset
- Future: We can implement backup codes

**Q: Patient trying to enable 2FA?**
- This is intentional - only doctors and nurses can use 2FA
- Returns 403 Forbidden

## 📖 Full Documentation

See `2FA_IMPLEMENTATION_GUIDE.md` for complete documentation including:
- Detailed API reference
- Frontend integration examples
- Security features
- Error handling
- Future enhancements

## 🎯 Next Steps

### For Frontend:
1. Add "Enable 2FA" button in settings
2. Show QR code in a modal when enabling
3. Add OTP input field during login
4. Add "Disable 2FA" option in settings

### Example UI Flow:
```
Settings Page
  └─ Security Settings
      ├─ Two-Factor Authentication: [Disabled]
      └─ [Enable 2FA Button]

Click Enable:
  └─ Show Modal
      ├─ Display QR Code
      ├─ Show Secret Key
      ├─ Instructions
      └─ OTP Input Field → [Verify Button]

Login (when 2FA enabled):
  └─ Email + Password
      └─ OTP Input Field
          └─ [Verify Button]
```

---

**Need Help?** Check `2FA_IMPLEMENTATION_GUIDE.md` or contact the dev team!

