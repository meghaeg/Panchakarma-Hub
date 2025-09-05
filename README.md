# Panchakarma Therapy Management Portal

A comprehensive web application for managing Panchakarma therapy services with role-based access for Patients, Centres, Doctors, and Ministry of Ayush administrators.

## Features

### 🎨 **Beautiful Ayurveda-themed UI**
- Dark Olive Green + Sandal color scheme
- Responsive Bootstrap design
- Modern glassmorphism effects
- Mobile-friendly interface

### 👥 **Role-based Access Control**
- **Patients**: Book appointments, track progress, submit feedback
- **Centres**: Manage doctors, handle bookings, assign treatments
- **Doctors**: Record vitals, track therapy progress, complete treatments
- **Ministry of Ayush**: Approve centres, monitor quality, handle complaints

### 🏥 **Core Functionality**
- NABH-accredited centre listings
- Appointment booking and management
- Real-time therapy progress tracking
- Email notifications for all major events
- Feedback and rating system
- Medical history and reports

## Technology Stack

- **Backend**: Python Flask
- **Database**: MongoDB Atlas
- **Frontend**: HTML5, CSS3, Bootstrap 5
- **Charts**: Chart.js
- **Email**: Python smtplib
- **Authentication**: Session-based with bcrypt

## Installation

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- Gmail account for email notifications

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Panchakarma
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure email settings**
   Edit `email_service.py` and update:
   ```python
   EMAIL_ADDRESS = "your-email@gmail.com"
   EMAIL_PASSWORD = "your-app-password"  # Use Gmail App Password
   ```

4. **Run the seed data script**
   ```bash
   python seed_data.py
   ```

5. **Start the application**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to: `http://localhost:5000`

## Default Login Credentials

### Admin (Ministry of Ayush)
- **Email**: admin@ayush.gov.in
- **Password**: admin123

### Sample Patients
- **Aadhar**: 123456789012, **Password**: patient123 (Arjun Patel)
- **Aadhar**: 123456789013, **Password**: patient123 (Meera Singh)
- **Aadhar**: 123456789014, **Password**: patient123 (Vikram Joshi)
- **Aadhar**: 123456789015, **Password**: patient123 (Kavya Menon)

### Sample Centres
- **Email**: info@keralaayurveda.com, **Password**: centre123
- **Email**: contact@rishikeshpanchakarma.com, **Password**: centre123
- **Email**: admin@bangaloreayurveda.com, **Password**: centre123

### Sample Doctors
- **Email**: dr.rajesh@keralaayurveda.com, **Password**: doctor123
- **Email**: dr.priya@keralaayurveda.com, **Password**: doctor123
- **Email**: dr.amit@rishikeshpanchakarma.com, **Password**: doctor123

## User Workflows

### 📋 **Patient Journey**
1. **Registration**: Sign up with Aadhar number and personal details
2. **Browse Centres**: View NABH-accredited centres by location
3. **Book Appointment**: Select therapy type, date, and time slot
4. **Receive Confirmation**: Email with appointment details and precautions
5. **Track Progress**: View daily progress updates and vitals
6. **Complete Therapy**: Receive summary report via email
7. **Submit Feedback**: Rate doctor and centre experience

### 🏥 **Centre Operations**
1. **Registration**: Apply for approval with license details
2. **Add Doctors**: Create doctor accounts and manage credentials
3. **Manage Bookings**: Assign doctors to patient appointments
4. **Monitor Progress**: Oversee ongoing treatments
5. **Handle Feedback**: Receive and respond to patient feedback

### 👩‍⚕️ **Doctor Workflow**
1. **View Patients**: Access assigned patient list and history
2. **Record Vitals**: Track BP, blood sugar, and other metrics
3. **Update Progress**: Add daily treatment notes and scores
4. **Complete Treatment**: Generate therapy summary and recommendations
5. **Email Reports**: Automatic patient notification on completion

### 🏛️ **Ministry of Ayush Admin**
1. **Review Applications**: Approve or reject centre registrations
2. **Monitor Quality**: Review patient feedback and complaints
3. **Take Actions**: Suspend centres based on poor performance
4. **Generate Reports**: Analytics on system performance

## Database Schema

### Collections
- **patients**: Patient profiles and medical history
- **centres**: Healthcare centre information and status
- **doctors**: Doctor profiles and specializations
- **appointments**: Treatment bookings and progress
- **feedback**: Patient ratings and comments
- **admin**: Ministry of Ayush administrator accounts

## API Endpoints

### Authentication
- `POST /auth/login` - User login
- `POST /auth/signup` - User registration
- `GET /auth/logout` - User logout

### Patient APIs
- `GET /patient/dashboard` - Patient dashboard
- `POST /patient/book-appointment` - Book new appointment
- `GET /patient/progress/<id>` - View therapy progress
- `POST /patient/feedback` - Submit feedback

### Centre APIs
- `GET /centre/dashboard` - Centre dashboard
- `POST /centre/add-doctor` - Add new doctor
- `POST /centre/assign-doctor` - Assign doctor to appointment

### Doctor APIs
- `GET /doctor/dashboard` - Doctor dashboard
- `GET /doctor/patient/<id>` - View patient details
- `POST /doctor/add-vitals` - Record patient vitals
- `POST /doctor/add-progress` - Add progress notes
- `POST /doctor/complete-therapy` - Complete treatment

### Admin APIs
- `GET /admin/dashboard` - Admin dashboard
- `POST /admin/approve-centre` - Approve/reject centre
- `POST /admin/suspend-centre` - Suspend centre

## Email Notifications

The system automatically sends emails for:
- ✅ Appointment confirmations with precautions
- 👨‍⚕️ Doctor assignment notifications
- 📋 Therapy completion summaries
- 📧 Follow-up reminders

## Security Features

- 🔐 Password hashing with bcrypt
- 🛡️ Session-based authentication
- 🔒 Role-based access control
- ✅ Input validation and sanitization
- 🌐 CORS protection

## Deployment

### Production Setup
1. Update MongoDB connection string
2. Configure production email credentials
3. Set environment variables
4. Use production WSGI server (Gunicorn)
5. Configure reverse proxy (Nginx)

### Environment Variables
```bash
FLASK_ENV=production
MONGO_URI=your-production-mongodb-uri
EMAIL_ADDRESS=your-production-email
EMAIL_PASSWORD=your-production-password
```

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and queries:
- 📧 Email: support@panchakarma-portal.com
- 📱 Phone: +91 1234567890
- 🌐 Website: https://panchakarma-portal.com

## Acknowledgments

- 🙏 Ministry of Ayush for guidelines
- 🏥 NABH for accreditation standards
- 📚 Ancient Ayurvedic texts and wisdom
- 👥 Healthcare professionals and patients

---

**Built with ❤️ for authentic Ayurvedic healing**
