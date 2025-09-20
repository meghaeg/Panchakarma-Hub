/**
 * WebSocket client for real-time dashboard updates
 * Connects to the WebSocket server and handles real-time updates
 */
class WebSocketManager {
    constructor(wsUrl = 'ws://localhost:8765') {
        this.wsUrl = wsUrl;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        this.reconnectInterval = 3000; // 3 seconds
        this.isConnected = false;
        this.eventHandlers = new Map();
        
        this.connect();
    }
    
    connect() {
        try {
            this.ws = new WebSocket(this.wsUrl);
            
            this.ws.onopen = (event) => {
                console.log('WebSocket connected');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.emit('connected', event);
            };
            
            this.ws.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.ws.onclose = (event) => {
                console.log('WebSocket disconnected');
                this.isConnected = false;
                this.emit('disconnected', event);
                
                // Attempt to reconnect
                if (this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                    setTimeout(() => this.connect(), this.reconnectInterval);
                } else {
                    console.error('Max reconnection attempts reached');
                    this.emit('reconnect_failed');
                }
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.emit('error', error);
            };
            
        } catch (error) {
            console.error('Error creating WebSocket connection:', error);
            this.emit('error', error);
        }
    }
    
    handleMessage(data) {
        console.log('Received WebSocket message:', data);
        
        switch (data.type) {
            case 'initial_data':
                this.handleInitialData(data.data);
                break;
            case 'update':
                this.handleUpdate(data.update_type, data.data);
                break;
            default:
                console.log('Unknown message type:', data.type);
        }
    }
    
    handleInitialData(data) {
        console.log('Received initial data:', data);
        
        // Update dashboard with initial data
        this.updateDashboardStats(data);
        this.updateRecentActivities(data.recent_activities || []);
        
        this.emit('initial_data', data);
    }
    
    handleUpdate(updateType, data) {
        console.log(`Received update: ${updateType}`, data);
        
        switch (updateType) {
            case 'doctor_added':
                this.handleDoctorAdded(data);
                break;
            case 'appointment_created':
                this.handleAppointmentCreated(data);
                break;
            case 'bed_status_changed':
                this.handleBedStatusChanged(data);
                break;
            case 'appointment_status_changed':
                this.handleAppointmentStatusChanged(data);
                break;
            default:
                console.log('Unknown update type:', updateType);
        }
        
        this.emit('update', { type: updateType, data });
    }
    
    handleDoctorAdded(data) {
        // Show notification
        this.showNotification('New Doctor Added', `Dr. ${data.name} has been added to the center`, 'success');
        
        // Update doctor list if it exists
        this.updateDoctorList(data);
        
        // Update statistics
        this.incrementCounter('total-doctors');
    }
    
    handleAppointmentCreated(data) {
        // Show notification
        this.showNotification('New Appointment', 'A new appointment has been created', 'info');
        
        // Update appointment list if it exists
        this.updateAppointmentList(data);
        
        // Update statistics
        this.incrementCounter('total-appointments');
        this.incrementCounter('today-appointments');
    }
    
    handleBedStatusChanged(data) {
        // Show notification
        const statusText = data.status === 'occupied' ? 'allocated' : 'freed';
        this.showNotification('Bed Status Changed', 
            `Bed ${data.room_number} has been ${statusText}${data.patient_name ? ` to ${data.patient_name}` : ''}`, 
            'info');
        
        // Update bed list if it exists
        this.updateBedList(data);
        
        // Update bed statistics
        this.updateBedStatistics();
    }
    
    handleAppointmentStatusChanged(data) {
        // Show notification
        this.showNotification('Appointment Status Changed', 
            `Appointment status changed to ${data.status}`, 'info');
        
        // Update appointment list if it exists
        this.updateAppointmentList(data);
    }
    
    updateDashboardStats(data) {
        // Update doctor statistics
        if (data.doctors) {
            this.updateElement('total-doctors', data.doctors.total);
        }
        
        // Update appointment statistics
        if (data.appointments) {
            this.updateElement('total-appointments', data.appointments.total);
            this.updateElement('today-appointments', data.appointments.today);
        }
        
        // Update bed statistics
        if (data.beds) {
            this.updateElement('total-beds', data.beds.total);
            this.updateElement('available-beds', data.beds.available);
            this.updateElement('occupied-beds', data.beds.occupied);
            this.updateElement('occupancy-rate', `${data.beds.occupancy_rate}%`);
        }
    }
    
    updateRecentActivities(activities) {
        const container = document.getElementById('recent-activities');
        if (!container) return;
        
        container.innerHTML = '';
        
        activities.forEach(activity => {
            const activityElement = this.createActivityElement(activity);
            container.appendChild(activityElement);
        });
    }
    
    createActivityElement(activity) {
        const div = document.createElement('div');
        div.className = 'activity-item';
        
        const time = new Date(activity.timestamp).toLocaleTimeString();
        const icon = this.getActivityIcon(activity.type);
        
        div.innerHTML = `
            <div class="activity-icon">${icon}</div>
            <div class="activity-content">
                <div class="activity-message">${activity.message}</div>
                <div class="activity-time">${time}</div>
            </div>
        `;
        
        return div;
    }
    
    getActivityIcon(type) {
        const icons = {
            'doctor_added': '👨‍⚕️',
            'appointment_created': '📅',
            'bed_allocated': '🛏️',
            'appointment_status_changed': '📋',
            'bed_status_changed': '🔄'
        };
        return icons[type] || '📢';
    }
    
    updateElement(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    incrementCounter(id) {
        const element = document.getElementById(id);
        if (element) {
            const currentValue = parseInt(element.textContent) || 0;
            element.textContent = currentValue + 1;
        }
    }
    
    updateDoctorList(data) {
        // This would update a doctor list table if it exists
        const doctorList = document.getElementById('doctor-list');
        if (doctorList) {
            // Add new doctor to the list
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${data.name}</td>
                <td>${data.specialization}</td>
                <td>${data.doctor_id}</td>
                <td><span class="badge badge-success">Active</span></td>
            `;
            doctorList.appendChild(row);
        }
    }
    
    updateAppointmentList(data) {
        // This would update an appointment list table if it exists
        const appointmentList = document.getElementById('appointment-list');
        if (appointmentList) {
            // Add new appointment to the list
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${data.appointment_id}</td>
                <td>${data.patient_id}</td>
                <td>${data.doctor_id}</td>
                <td><span class="badge badge-info">${data.status}</span></td>
            `;
            appointmentList.appendChild(row);
        }
    }
    
    updateBedList(data) {
        // This would update a bed list table if it exists
        const bedList = document.getElementById('bed-list');
        if (bedList) {
            // Find and update the bed row
            const rows = bedList.querySelectorAll('tr');
            for (let row of rows) {
                const bedIdCell = row.querySelector('td:first-child');
                if (bedIdCell && bedIdCell.textContent === data.bed_id) {
                    const statusCell = row.querySelector('.bed-status');
                    if (statusCell) {
                        statusCell.textContent = data.status;
                        statusCell.className = `bed-status badge badge-${data.status === 'available' ? 'success' : 'warning'}`;
                    }
                    break;
                }
            }
        }
    }
    
    updateBedStatistics() {
        // Refresh bed statistics by making an API call
        fetch('/api/bed-statistics')
            .then(response => response.json())
            .then(data => {
                this.updateElement('total-beds', data.total);
                this.updateElement('available-beds', data.available);
                this.updateElement('occupied-beds', data.occupied);
                this.updateElement('occupancy-rate', `${data.occupancy_rate}%`);
            })
            .catch(error => console.error('Error updating bed statistics:', error));
    }
    
    showNotification(title, message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <div class="notification-title">${title}</div>
                <div class="notification-message">${message}</div>
            </div>
            <button class="notification-close" onclick="this.parentElement.remove()">×</button>
        `;
        
        // Add to notification container
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            document.body.appendChild(container);
        }
        
        container.appendChild(notification);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    }
    
    // Event handling
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }
    
    emit(event, data) {
        if (this.eventHandlers.has(event)) {
            this.eventHandlers.get(event).forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error('Error in event handler:', error);
                }
            });
        }
    }
    
    // Public methods
    send(message) {
        if (this.ws && this.isConnected) {
            this.ws.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected');
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
}

// Initialize WebSocket manager when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on a dashboard page
    if (document.body.classList.contains('dashboard-page')) {
        const wsManager = new WebSocketManager();
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', function() {
            if (document.hidden) {
                // Page is hidden, pause updates
                console.log('Page hidden, pausing WebSocket updates');
            } else {
                // Page is visible, resume updates
                console.log('Page visible, resuming WebSocket updates');
            }
        });
        
        // Make wsManager globally available
        window.wsManager = wsManager;
    }
});

// CSS for notifications
const notificationStyles = `
<style>
.notification-container {
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 9999;
    max-width: 400px;
}

.notification {
    display: flex;
    align-items: center;
    padding: 12px 16px;
    margin-bottom: 10px;
    border-radius: 4px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    animation: slideIn 0.3s ease-out;
}

.notification-success {
    background-color: #d4edda;
    border-left: 4px solid #28a745;
    color: #155724;
}

.notification-info {
    background-color: #d1ecf1;
    border-left: 4px solid #17a2b8;
    color: #0c5460;
}

.notification-warning {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
    color: #856404;
}

.notification-error {
    background-color: #f8d7da;
    border-left: 4px solid #dc3545;
    color: #721c24;
}

.notification-content {
    flex: 1;
}

.notification-title {
    font-weight: bold;
    margin-bottom: 4px;
}

.notification-message {
    font-size: 14px;
}

.notification-close {
    background: none;
    border: none;
    font-size: 18px;
    cursor: pointer;
    margin-left: 10px;
    opacity: 0.7;
}

.notification-close:hover {
    opacity: 1;
}

@keyframes slideIn {
    from {
        transform: translateX(100%);
        opacity: 0;
    }
    to {
        transform: translateX(0);
        opacity: 1;
    }
}

.activity-item {
    display: flex;
    align-items: center;
    padding: 8px 0;
    border-bottom: 1px solid #eee;
}

.activity-icon {
    font-size: 20px;
    margin-right: 12px;
}

.activity-content {
    flex: 1;
}

.activity-message {
    font-size: 14px;
    margin-bottom: 2px;
}

.activity-time {
    font-size: 12px;
    color: #666;
}
</style>
`;

// Inject notification styles
document.head.insertAdjacentHTML('beforeend', notificationStyles);
