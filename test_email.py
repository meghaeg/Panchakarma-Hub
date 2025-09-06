#!/usr/bin/env python3
"""
Email Service Test Script
This script tests the email functionality of the Panchakarma Therapy Management Portal
"""

from email_service import test_email_connection, send_test_email, EMAIL_ADDRESS, EMAIL_PASSWORD

def main():
    print("=" * 60)
    print("PANCHAKARMA THERAPY MANAGEMENT PORTAL")
    print("EMAIL SERVICE TEST")
    print("=" * 60)
    
    print(f"Email Configuration:")
    print(f"  From: {EMAIL_ADDRESS}")
    print(f"  Password: {'*' * len(EMAIL_PASSWORD)}")
    print()
    
    # Test 1: Email Connection
    print("Test 1: Testing email connection...")
    if test_email_connection():
        print("✅ Email connection successful!")
    else:
        print("❌ Email connection failed!")
        print("Please check your email credentials and app password.")
        return
    
    print()
    
    # Test 2: Send test email
    test_email = input("Enter your email address to receive a test email: ").strip()
    
    if not test_email:
        print("No email address provided. Skipping test email.")
        return
    
    print(f"\nTest 2: Sending test email to {test_email}...")
    if send_test_email(test_email):
        print("✅ Test email sent successfully!")
        print(f"Please check your inbox at {test_email}")
    else:
        print("❌ Failed to send test email!")
    
    print("\n" + "=" * 60)
    print("Email service test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
