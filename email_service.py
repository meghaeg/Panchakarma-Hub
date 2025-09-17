import smtplib
from datetime import datetime
import os

# Simple email classes for compatibility
class MimeText:
    def __init__(self, body, subtype='plain'):
        self.body = body
        self.subtype = subtype
        self._headers = {}
    
    def __setitem__(self, key, value):
        self._headers[key] = value
    
    def as_string(self):
        headers = '\n'.join([f'{k}: {v}' for k, v in self._headers.items()])
        return f"{headers}\n\n{self.body}"

class MimeMultipart:
    def __init__(self, subtype='mixed'):
        self.subtype = subtype
        self._headers = {}
        self._parts = []
    
    def __setitem__(self, key, value):
        self._headers[key] = value
    
    def attach(self, part):
        self._parts.append(part)
    
    def as_string(self):
        headers = '\n'.join([f'{k}: {v}' for k, v in self._headers.items()])
        body = '\n'.join([part.as_string() if hasattr(part, 'as_string') else str(part) for part in self._parts])
        return f"{headers}\n\n{body}"

# Email configuration
try:
    from email_config import EMAIL_CONFIG
    SMTP_SERVER = EMAIL_CONFIG['smtp_server']
    SMTP_PORT = EMAIL_CONFIG['smtp_port']
    EMAIL_ADDRESS = EMAIL_CONFIG['email_address']
    EMAIL_PASSWORD = EMAIL_CONFIG['email_password']
    TESTING_MODE = EMAIL_CONFIG['testing_mode']
except ImportError:
    # Fallback configuration
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587
    EMAIL_ADDRESS = "meghaeg27@gmail.com"
    EMAIL_PASSWORD = "YOUR_APP_PASSWORD_HERE"  # Replace with Gmail App Password
    TESTING_MODE = False

def send_email(to_email, subject, body, is_html=False):
    """Send email notification"""
    if TESTING_MODE:
        # In testing mode, just log the email details instead of sending
        print(f"\n{'='*50}")
        print(f"EMAIL SIMULATION - Would send to: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print(f"{'='*50}\n")
        return True
    
    try:
        # Validate email address
        if not to_email or '@' not in to_email:
            print(f"Invalid email address: {to_email}")
            return False
        
        # Create message
        msg = MimeMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        # Add body to email
        if is_html:
            msg.attach(MimeText(body, 'html'))
        else:
            msg.attach(MimeText(body, 'plain'))
        
        # Create SMTP session
        print(f"Attempting to send email to: {to_email}")
        print(f"Subject: {subject}")
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Enable security
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        # Send email
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        
        print(f"✅ Email sent successfully to: {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ SMTP Authentication Error: {e}")
        print("Please check your email credentials and app password")
        return False
    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ SMTP Recipients Refused: {e}")
        print(f"Invalid recipient email: {to_email}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        print(f"❌ SMTP Server Disconnected: {e}")
        print("Server connection lost")
        return False
    except smtplib.SMTPException as e:
        print(f"❌ SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"❌ General Email Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_email_connection():
    """Test email connection and credentials"""
    try:
        print("Testing email connection...")
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.quit()
        print("✅ Email connection test successful!")
        return True
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Email authentication failed: {e}")
        print("Please check your email credentials and app password")
        return False
    except Exception as e:
        print(f"❌ Email connection test failed: {e}")
        return False

def send_test_email(test_email):
    """Send a test email to verify the service works"""
    subject = "Test Email - Panchakarma Therapy Management Portal"
    body = f"""
    This is a test email from the Panchakarma Therapy Management Portal.
    
    If you receive this email, the notification system is working correctly!
    
    Test Details:
    - Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    - From: {EMAIL_ADDRESS}
    - To: {test_email}
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    
    print(f"Sending test email to: {test_email}")
    return send_email(test_email, subject, body)

def send_appointment_confirmation(patient_email, patient_name, appointment_details):
    """Send appointment confirmation email"""
    subject = "Panchakarma Therapy Appointment Confirmation"
    
    body = f"""
    Dear {patient_name},
    
    Your Panchakarma therapy appointment has been confirmed!
    
    Appointment Details:
    - Appointment ID: {appointment_details['appointment_id']}
    - Centre: {appointment_details['centre_name']}
    - Date: {appointment_details['date']}
    - Time: {appointment_details['time']}
    - Therapy Type: {appointment_details['therapy_type']}
    
    Pre-Procedure Precautions:
    1. Avoid heavy meals 3 hours before the therapy
    2. Wear comfortable, loose-fitting clothes
    3. Inform the doctor about any medications you are taking
    4. Avoid alcohol and smoking 24 hours before therapy
    5. Get adequate rest the night before
    6. Arrive 15 minutes early for registration
    
    Please bring:
    - Valid ID proof
    - Previous medical reports (if any)
    - List of current medications
    
    For any queries, please contact the centre directly.
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    
    return send_email(patient_email, subject, body)

def send_therapy_summary(patient_email, patient_name, summary_details):
    """Send therapy completion summary"""
    subject = "Panchakarma Therapy Completion Summary"
    
    body = f"""
    Dear {patient_name},
    
    Congratulations on completing your Panchakarma therapy!
    
    Therapy Summary:
    - Patient ID: {summary_details['patient_id']}
    - Therapy Type: {summary_details['therapy_type']}
    - Duration: {summary_details['duration']} days
    - Doctor: Dr. {summary_details['doctor_name']}
    - Centre: {summary_details['centre_name']}
    - Completion Date: {summary_details['completion_date']}
    
    Treatment Progress:
    {summary_details['progress_summary']}
    
    Final Vitals:
    - Blood Pressure: {summary_details.get('final_bp', 'Not recorded')}
    - Blood Sugar: {summary_details.get('final_sugar', 'Not recorded')}
    
    Post-Therapy Recommendations:
    {summary_details.get('recommendations', 'Follow general Ayurvedic lifestyle practices')}
    
    Next Session Schedule:
    {summary_details.get('next_session', 'To be determined based on progress')}
    
    Thank you for choosing our Panchakarma therapy services.
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    
    return send_email(patient_email, subject, body)

def send_doctor_assignment(patient_email, patient_name, doctor_details):
    """Send doctor assignment notification"""
    subject = "Doctor Assigned for Your Panchakarma Therapy"
    
    body = f"""
    Dear {patient_name},
    
    A doctor has been assigned for your upcoming Panchakarma therapy.
    
    Doctor Details:
    - Name: Dr. {doctor_details['name']}
    - Specialization: {doctor_details['specialization']}
    - Experience: {doctor_details['experience']} years
    - Qualification: {doctor_details['qualification']}
    
    Your therapy will begin as scheduled. The doctor will review your medical history and customize the treatment plan accordingly.
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    
    return send_email(patient_email, subject, body)

def send_appointment_notification_to_centre(centre_id, appointment_data):
    """Send appointment notification to centre for approval"""
    # This would need centre email lookup - simplified for now
    subject = "New Appointment Request - Approval Required"
    body = f"""
    New appointment request received:
    
    Appointment ID: {appointment_data['appointment_id']}
    Patient ID: {appointment_data['patient_id']}
    Therapy Type: {appointment_data['therapy_type']}
    Date: {appointment_data['appointment_date']}
    Time: {appointment_data['time_slot']}
    
    Please log in to approve or reject this appointment.
    """
    return send_email("centre@example.com", subject, body)

def send_appointment_confirmation_to_patient(appointment_data):
    """Send appointment confirmation to patient"""
    subject = "Appointment Confirmed - Panchakarma Portal"
    body = f"""
    Dear Patient,
    
    Your appointment has been confirmed!
    
    Appointment Details:
    - Appointment ID: {appointment_data['appointment_id']}
    - Date: {appointment_data['appointment_date']}
    - Time: {appointment_data['time_slot']}
    - Therapy Type: {appointment_data['therapy_type']}
    - Assigned Doctor: {appointment_data.get('assigned_doctor', 'TBD')}
    
    Please arrive 15 minutes before your scheduled time.
    
    Best regards,
    Panchakarma Portal Team
    """
    return send_email("patient@example.com", subject, body)

def send_appointment_rejection_to_patient(appointment_data):
    """Send appointment rejection to patient"""
    subject = "Appointment Request - Update Required"
    body = f"""
    Dear Patient,
    
    We regret to inform you that your appointment request could not be confirmed for the selected date and time.
    
    Appointment ID: {appointment_data['appointment_id']}
    Requested Date: {appointment_data['appointment_date']}
    Requested Time: {appointment_data['time_slot']}
    
    Please try booking for a different date or time slot.
    
    Best regards,
    Panchakarma Portal Team
    """
    return send_email("patient@example.com", subject, body)

def send_post_therapy_email(appointment_id, therapy_report):
    """Send post-therapy progress email to patient"""
    subject = "Therapy Completed - Progress Report & Instructions"
    body = f"""
    Dear Patient,
    
    Your Panchakarma therapy session has been completed successfully!
    
    Progress Report:
    {therapy_report['progress_notes']}
    
    Prescribed Medications:
    {therapy_report['medications'] or 'None prescribed'}
    
    Post-Therapy Instructions:
    {therapy_report['after_therapy_instructions']}
    
    Next Session Recommendation:
    {therapy_report['next_session_recommendation'] or 'No immediate follow-up required'}
    
    Please follow the instructions carefully for optimal results.
    
    Best regards,
    Your Panchakarma Care Team
    """
    return send_email("patient@example.com", subject, body)

def send_therapy_summary(patient_email, patient_name, summary_details):
    """Send therapy completion summary"""
    subject = "Panchakarma Therapy Completion Summary"
    body = f"""
    Dear {patient_name},
    
    Congratulations on completing your Panchakarma therapy!
    
    Therapy Summary:
    - Patient ID: {summary_details['patient_id']}
    - Therapy Type: {summary_details['therapy_type']}
    - Duration: {summary_details['duration']} days
    - Doctor: Dr. {summary_details['doctor_name']}
    - Centre: {summary_details['centre_name']}
    - Completion Date: {summary_details['completion_date']}
    
    Treatment Progress:
    {summary_details['progress_summary']}
    
    Post-Therapy Recommendations:
    {summary_details.get('recommendations', 'Follow general Ayurvedic lifestyle practices')}
    
    Next Session Schedule:
    {summary_details.get('next_session', 'To be determined based on progress')}
    
    Thank you for choosing our Panchakarma therapy services.
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    return send_email(patient_email, subject, body)


def send_detox_appointment_approval_notification(patient_email, patient_name, appointment_data, doctor_name, therapy_time):
    """Send detox appointment approval notification"""
    subject = f"✅ Detox Therapy Approved - {appointment_data['schedule']['plan_info']['name']}"
    
    body = f"""
    Dear {patient_name},
    
    🎉 Great news! Your detox therapy appointment has been approved and scheduled.
    
    📋 Appointment Details:
    • Therapy: {appointment_data['schedule']['plan_info']['name']}
    • Duration: {appointment_data['schedule']['plan_info']['duration']} days
    • Start Date: {appointment_data['start_date']}
    • Therapy Time: {therapy_time}
    • Assigned Doctor: Dr. {doctor_name}
    • Centre: {appointment_data.get('centre_name', 'Your selected centre')}
    
    📅 What's Next:
    1. Arrive 15 minutes before your scheduled therapy time
    2. Bring a valid ID and any medical reports
    3. Follow the pre-therapy precautions (see below)
    
    ⚠️ Important Pre-Therapy Precautions:
    • Avoid heavy meals 2 hours before therapy
    • Stay hydrated throughout the day
    • Inform your doctor about any medications you're taking
    • Wear comfortable, loose-fitting clothing
    • Avoid alcohol and smoking 24 hours before therapy
    
    📱 Access Your Schedule:
    You can view your detailed daily schedule and track your progress through your patient dashboard.
    
    If you have any questions or need to reschedule, please contact your centre immediately.
    
    We look forward to supporting your wellness journey!
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    return send_email(patient_email, subject, body)


def send_detox_appointment_rejection_notification(patient_email, patient_name, appointment_data, reason=None):
    """Send detox appointment rejection notification"""
    subject = f"❌ Detox Therapy Request Update - {appointment_data['schedule']['plan_info']['name']}"
    
    body = f"""
    Dear {patient_name},
    
    We regret to inform you that your detox therapy request could not be approved at this time.
    
    📋 Request Details:
    • Therapy: {appointment_data['schedule']['plan_info']['name']}
    • Requested Start Date: {appointment_data['start_date']}
    • Centre: {appointment_data.get('centre_name', 'Your selected centre')}
    
    {f"Reason: {reason}" if reason else "Please contact your centre for more information about this decision."}
    
    🔄 Next Steps:
    1. You may submit a new request with different dates
    2. Contact your centre to discuss alternative options
    3. Consider consulting with our doctors for personalized recommendations
    
    We apologize for any inconvenience and appreciate your understanding.
    
    If you have any questions, please don't hesitate to contact us.
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    return send_email(patient_email, subject, body)


def send_pre_therapy_precautions_notification(patient_email, patient_name, appointment_data, days_before=1):
    """Send pre-therapy precautions notification"""
    subject = f"⚠️ Pre-Therapy Precautions - Starting Tomorrow!"
    
    body = f"""
    Dear {patient_name},
    
    Your detox therapy begins tomorrow! Please review these important precautions.
    
    📅 Therapy Details:
    • Therapy: {appointment_data['schedule']['plan_info']['name']}
    • Start Date: {appointment_data['start_date']}
    • Duration: {appointment_data['schedule']['plan_info']['duration']} days
    • Doctor: Dr. {appointment_data.get('assigned_doctor', 'To be assigned')}
    
    🚨 CRITICAL Pre-Therapy Precautions:
    
    📋 Dietary Guidelines:
    • Avoid heavy, oily, or spicy foods today
    • Eat light, easily digestible meals
    • Avoid dairy products and cold foods
    • Stay hydrated with warm water
    • No alcohol or smoking for 24 hours
    
    🏥 Medical Preparations:
    • Inform your doctor about all current medications
    • Bring any recent medical reports
    • Get adequate rest tonight (8+ hours sleep)
    • Avoid strenuous physical activities
    
    👕 What to Bring:
    • Comfortable, loose-fitting clothing
    • Valid ID and insurance documents
    • List of current medications
    • Any relevant medical reports
    
    ⏰ Arrival Instructions:
    • Arrive 15 minutes before your scheduled time
    • Come with an empty stomach (no food 2 hours before)
    • Bring a positive mindset and patience
    
    📱 Emergency Contact:
    If you have any concerns or questions, contact your centre immediately.
    
    Remember: This therapy is designed to cleanse and rejuvenate your body. Follow these precautions for the best results.
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    return send_email(patient_email, subject, body)


def send_post_therapy_precautions_notification(patient_email, patient_name, appointment_data):
    """Send post-therapy precautions notification"""
    subject = f"🏁 Post-Therapy Care Instructions - {appointment_data['schedule']['plan_info']['name']}"
    
    body = f"""
    Dear {patient_name},
    
    Congratulations on completing your detox therapy! Here are important post-therapy care instructions.
    
    📅 Therapy Completed:
    • Therapy: {appointment_data['schedule']['plan_info']['name']}
    • Duration: {appointment_data['schedule']['plan_info']['duration']} days
    • Completion Date: {datetime.now().strftime('%Y-%m-%d')}
    
    🏥 Post-Therapy Care Instructions:
    
    📋 Dietary Guidelines (Next 7 Days):
    • Start with light, easily digestible foods
    • Gradually reintroduce regular foods
    • Avoid heavy, oily, or spicy foods initially
    • Include fresh fruits and vegetables
    • Stay hydrated with warm water
    • Avoid cold drinks and ice cream
    
    🚫 Restrictions:
    • No alcohol for at least 7 days
    • Avoid smoking for 7 days
    • No strenuous exercise for 3 days
    • Avoid exposure to extreme temperatures
    • Limit screen time and stress
    
    💊 Medication:
    • Continue any prescribed medications
    • Take any recommended supplements
    • Follow your doctor's specific instructions
    
    📈 Recovery Tips:
    • Get adequate rest (8+ hours sleep)
    • Practice gentle yoga or meditation
    • Take warm baths with Epsom salts
    • Stay positive and patient with recovery
    
    🔄 Follow-up:
    • Schedule follow-up appointment as recommended
    • Monitor your progress and report any concerns
    • Continue healthy lifestyle practices
    
    📱 Support:
    If you experience any unusual symptoms or have questions, contact your doctor immediately.
    
    Your body has undergone a significant cleansing process. Give it time to adjust and continue your wellness journey.
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    return send_email(patient_email, subject, body)


def send_daily_therapy_reminder(patient_email, patient_name, appointment_data, day_number):
    """Send daily therapy reminder"""
    subject = f"📅 Daily Therapy Reminder - Day {day_number}"
    
    body = f"""
    Dear {patient_name},
    
    This is your daily reminder for your detox therapy session.
    
    📅 Today's Session:
    • Day: {day_number} of {appointment_data['schedule']['plan_info']['duration']}
    • Therapy: {appointment_data['schedule']['plan_info']['name']}
    • Time: {appointment_data['therapy_time']}
    • Doctor: Dr. {appointment_data.get('assigned_doctor', 'Your assigned doctor')}
    
    💡 Today's Focus:
    Continue following your therapy schedule and maintain the dietary guidelines.
    
    📱 Track Your Progress:
    Log into your patient dashboard to:
    • View today's therapy schedule
    • Track your daily progress
    • See your vitals and improvement scores
    • Read notes from your doctor
    
    ⚠️ Remember:
    • Arrive on time for your session
    • Follow all dietary restrictions
    • Stay hydrated throughout the day
    • Report any concerns to your doctor
    
    You're doing great! Keep up the excellent work on your wellness journey.
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    return send_email(patient_email, subject, body)


def send_doctor_assignment_notification(doctor_email, doctor_name, appointment_data, patient_name):
    """Send doctor assignment notification"""
    subject = f"👨‍⚕️ New Detox Therapy Assignment - {appointment_data['schedule']['plan_info']['name']}"
    
    body = f"""
    Dear Dr. {doctor_name},
    
    You have been assigned a new detox therapy patient.
    
    📋 Patient Details:
    • Name: {patient_name}
    • Therapy: {appointment_data['schedule']['plan_info']['name']}
    • Duration: {appointment_data['schedule']['plan_info']['duration']} days
    • Start Date: {appointment_data['start_date']}
    • Therapy Time: {appointment_data['therapy_time']}
    
    📅 Your Responsibilities:
    1. Review the patient's medical history
    2. Conduct initial assessment
    3. Monitor daily progress and vitals
    4. Update therapy schedule as needed
    5. Provide guidance and support
    
    📱 Access Patient Information:
    Log into your doctor dashboard to:
    • View detailed patient information
    • Access therapy schedule
    • Update progress and vitals
    • Add notes and observations
    
    ⚠️ Important Notes:
    • Follow all safety precautions
    • Document all observations
    • Communicate regularly with the patient
    • Report any concerns to the centre
    
    Thank you for your dedication to patient care.
    
    Best regards,
    Panchakarma Therapy Management Portal
    """
    return send_email(doctor_email, subject, body)


def send_zoom_request_to_centre(centre_email, centre_name, patient_name, date_str, slot):
    subject = "New Zoom Meeting Request - Approval Required"
    body = f"""
    Dear {centre_name},
    
    A patient has requested a Zoom tele-consultation for today.
    
    Details:
    - Patient: {patient_name}
    - Date: {date_str}
    - Slot: {slot}
    
    Please approve in your dashboard and assign a doctor.
    
    Best regards,
    Panchakarma Portal
    """
    return send_email(centre_email, subject, body)


def send_zoom_approval_emails(patient_email, patient_name, doctor_email, doctor_name, date_str, slot, join_url, start_url):
    # Patient email
    p_subject = "Your Zoom Consultation is Scheduled"
    p_body = f"""
    Dear {patient_name},
    
    Your Zoom consultation has been scheduled.
    
    - Date: {date_str}
    - Time: {slot}
    - Doctor: Dr. {doctor_name}
    - Join Link: {join_url}
    
    Please join a few minutes early.
    
    Best regards,
    Panchakarma Portal
    """
    send_email(patient_email, p_subject, p_body)

    # Doctor email
    d_subject = "Zoom Consultation Assigned"
    d_body = f"""
    Dear Dr. {doctor_name},
    
    A Zoom consultation has been assigned to you.
    
    - Patient: {patient_name}
    - Date: {date_str}
    - Time: {slot}
    - Start URL: {start_url}
    
    Please start the meeting at the scheduled time.
    """
    return send_email(doctor_email, d_subject, d_body)