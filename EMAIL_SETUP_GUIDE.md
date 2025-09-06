# 📧 Email Service Setup Guide

## Problem
The email service is not sending emails because Gmail requires App Passwords for SMTP authentication.

## Solution

### Step 1: Enable 2-Factor Authentication
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable "2-Step Verification" if not already enabled

### Step 2: Generate Gmail App Password
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Click on "2-Step Verification"
3. Scroll down to "App passwords"
4. Click "App passwords"
5. Select "Mail" as the app
6. Select "Other (Custom name)" as the device
7. Enter "Panchakarma Portal" as the name
8. Click "Generate"
9. Copy the 16-character password (format: `abcd efgh ijkl mnop`)

### Step 3: Update Email Configuration
1. Open `email_service.py`
2. Replace `YOUR_APP_PASSWORD_HERE` with your actual App Password
3. Save the file

### Step 4: Test Email Service
Run the test script:
```bash
python test_email.py
```

### Alternative: Use Different Email Service
If you prefer not to use Gmail, you can use other email services:

#### Option 1: Outlook/Hotmail
```python
SMTP_SERVER = "smtp-mail.outlook.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your-email@outlook.com"
EMAIL_PASSWORD = "your-password"
```

#### Option 2: Yahoo Mail
```python
SMTP_SERVER = "smtp.mail.yahoo.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your-email@yahoo.com"
EMAIL_PASSWORD = "your-app-password"
```

## Testing
After updating the credentials, test the email service:

1. **Test Connection:**
   ```python
   from email_service import test_email_connection
   test_email_connection()
   ```

2. **Send Test Email:**
   ```python
   from email_service import send_test_email
   send_test_email("recipient@example.com")
   ```

3. **Test in Application:**
   - Start the Flask app
   - Go to patient dashboard
   - Book a detox therapy
   - Check if approval emails are sent

## Troubleshooting

### Common Issues:
1. **Authentication Error**: Use App Password, not regular password
2. **Connection Refused**: Check firewall settings
3. **Invalid Recipient**: Verify email address format
4. **SMTP Server Error**: Try different SMTP server/port

### Debug Mode:
To see detailed email logs, check the console output when sending emails.

## Security Notes:
- Never commit App Passwords to version control
- Use environment variables for production
- Regularly rotate App Passwords
- Monitor email sending logs

## Email Templates Available:
- ✅ Detox Therapy Approval
- ❌ Detox Therapy Rejection  
- ⚠️ Pre-Therapy Precautions
- 🏁 Post-Therapy Care Instructions
- 📅 Daily Therapy Reminders
- 👨‍⚕️ Doctor Assignment Notifications

All templates include comprehensive information and professional formatting.
