"""
Email Configuration File
Update these settings to configure your email service
"""

# Gmail Configuration (Recommended)
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',
    'smtp_port': 587,
    'email_address': 'meghaeg27@gmail.com',
    'email_password': 'tyih jjke xchu cmlg',  # Replace with Gmail App Password
    'testing_mode': False  # Set to True to simulate emails without sending
}

# Alternative Email Services (Uncomment to use)

# Outlook/Hotmail Configuration
# EMAIL_CONFIG = {
#     'smtp_server': 'smtp-mail.outlook.com',
#     'smtp_port': 587,
#     'email_address': 'your-email@outlook.com',
#     'email_password': 'your-password',
#     'testing_mode': False
# }

# Yahoo Mail Configuration
# EMAIL_CONFIG = {
#     'smtp_server': 'smtp.mail.yahoo.com',
#     'smtp_port': 587,
#     'email_address': 'your-email@yahoo.com',
#     'email_password': 'your-app-password',
#     'testing_mode': False
# }

# Instructions:
# 1. For Gmail: Generate an App Password (16 characters)
# 2. Replace 'YOUR_APP_PASSWORD_HERE' with your actual App Password
# 3. Set 'testing_mode': False to enable real email sending
# 4. Run 'python test_email.py' to test the configuration
