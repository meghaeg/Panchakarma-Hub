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
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "meghaeg27@gmail.com"  # Replace with actual email
EMAIL_PASSWORD = "Megha2711$"  # Replace with actual app password

# For testing purposes, we'll simulate email sending
TESTING_MODE = True

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
        msg = MimeMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        
        if is_html:
            msg.attach(MimeText(body, 'html'))
        else:
            msg.attach(MimeText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, to_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Email sending failed: {e}")
        return False

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
