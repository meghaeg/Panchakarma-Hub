// Bed Management JavaScript Functions
class BedManager {
    constructor() {
        this.beds = [];
        this.stats = {};
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.loadBeds();
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Filter event listeners
        document.getElementById('bedTypeFilter')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('statusFilter')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('roomFilter')?.addEventListener('input', () => this.applyFilters());
        document.getElementById('patientFilter')?.addEventListener('input', () => this.applyFilters());

        // Patient search
        document.getElementById('patientSearch')?.addEventListener('input', (e) => this.searchPatients(e.target.value));
    }

    async loadBeds() {
        try {
            const response = await fetch('/centre/api/beds');
            const data = await response.json();
            
            if (data.success) {
                this.beds = data.beds;
                this.renderBedGrid();
                this.updateBedTable();
            }
        } catch (error) {
            console.error('Error loading beds:', error);
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/centre/api/bed-stats');
            const data = await response.json();
            
            if (data.success) {
                this.stats = data.stats;
                this.updateStatsDisplay();
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    renderBedGrid() {
        const bedGrid = document.getElementById('bedGrid');
        if (!bedGrid) return;

        bedGrid.innerHTML = '';
        
        this.beds.forEach(bed => {
            const bedCard = this.createBedCard(bed);
            bedGrid.appendChild(bedCard);
        });
    }

    createBedCard(bed) {
        const card = document.createElement('div');
        card.className = `bed-card ${bed.status}`;
        card.setAttribute('data-bed-id', bed.bed_id);
        
        const statusIcon = this.getStatusIcon(bed.status);
        const statusColor = this.getStatusColor(bed.status);
        
        card.innerHTML = `
            <div class="bed-icon" style="color: ${statusColor}">${statusIcon}</div>
            <div class="bed-id">${bed.bed_id}</div>
            <div class="bed-type">${bed.bed_type.replace('_', ' ').toUpperCase()}</div>
            <div class="bed-room">Room: ${bed.room_number}</div>
            ${bed.current_patient_name ? `<div class="bed-patient">${bed.current_patient_name}</div>` : ''}
        `;
        
        card.onclick = () => this.viewBedDetails(bed.bed_id);
        
        return card;
    }

    getStatusIcon(status) {
        const icons = {
            'available': '🟢',
            'occupied': '🔴',
            'under_cleaning': '🟡',
            'reserved': '🔵'
        };
        return icons[status] || '⚪';
    }

    getStatusColor(status) {
        const colors = {
            'available': '#28a745',
            'occupied': '#dc3545',
            'under_cleaning': '#ffc107',
            'reserved': '#17a2b8'
        };
        return colors[status] || '#6c757d';
    }

    updateBedTable() {
        const tbody = document.querySelector('#bedTable tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        
        this.beds.forEach(bed => {
            const row = document.createElement('tr');
            row.setAttribute('data-bed-id', bed.bed_id);
            row.innerHTML = `
                <td><strong>${bed.bed_id}</strong></td>
                <td><span class="badge bg-info">${bed.bed_type.replace('_', ' ').title()}</span></td>
                <td>${bed.room_number}</td>
                <td><span class="status-badge status-${bed.status}">${bed.status.replace('_', ' ').title()}</span></td>
                <td>${bed.current_patient_name || '<span class="text-muted">-</span>'}</td>
                <td>₹${bed.price_per_day}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        ${this.getActionButtons(bed)}
                    </div>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    getActionButtons(bed) {
        let buttons = '';
        
        if (bed.status === 'available') {
            buttons += `<button class="btn btn-success" onclick="bedManager.allocateBed('${bed.bed_id}')"><i class="fas fa-user-plus"></i> Allocate</button>`;
            buttons += `<button class="btn btn-warning" onclick="bedManager.reserveBed('${bed.bed_id}')"><i class="fas fa-bookmark"></i> Reserve</button>`;
        } else if (bed.status === 'occupied') {
            buttons += `<button class="btn btn-danger" onclick="bedManager.checkoutBed('${bed.bed_id}')"><i class="fas fa-sign-out-alt"></i> Checkout</button>`;
        } else if (bed.status === 'under_cleaning') {
            buttons += `<button class="btn btn-success" onclick="bedManager.markAvailable('${bed.bed_id}')"><i class="fas fa-check"></i> Mark Available</button>`;
        } else if (bed.status === 'reserved') {
            buttons += `<button class="btn btn-primary" onclick="bedManager.allocateBed('${bed.bed_id}')"><i class="fas fa-user-plus"></i> Allocate</button>`;
            buttons += `<button class="btn btn-danger" onclick="bedManager.cancelReservation('${bed.bed_id}')"><i class="fas fa-times"></i> Cancel</button>`;
        }
        
        buttons += `<button class="btn btn-outline-info" onclick="bedManager.viewBedDetails('${bed.bed_id}')"><i class="fas fa-eye"></i> View</button>`;
        
        return buttons;
    }

    updateStatsDisplay() {
        // Update statistics cards if they exist
        const totalElement = document.querySelector('[data-stat="total"]');
        const availableElement = document.querySelector('[data-stat="available"]');
        const occupiedElement = document.querySelector('[data-stat="occupied"]');
        const cleaningElement = document.querySelector('[data-stat="under_cleaning"]');
        const reservedElement = document.querySelector('[data-stat="reserved"]');

        if (totalElement) totalElement.textContent = this.stats.total || 0;
        if (availableElement) availableElement.textContent = this.stats.available || 0;
        if (occupiedElement) occupiedElement.textContent = this.stats.occupied || 0;
        if (cleaningElement) cleaningElement.textContent = this.stats.under_cleaning || 0;
        if (reservedElement) reservedElement.textContent = this.stats.reserved || 0;
    }

    async applyFilters() {
        const filters = {
            bed_type: document.getElementById('bedTypeFilter')?.value,
            status: document.getElementById('statusFilter')?.value,
            room_number: document.getElementById('roomFilter')?.value,
            patient_name: document.getElementById('patientFilter')?.value
        };
        
        // Remove empty filters
        Object.keys(filters).forEach(key => {
            if (!filters[key]) delete filters[key];
        });
        
        const queryString = new URLSearchParams(filters).toString();
        
        try {
            const response = await fetch(`/centre/api/beds?${queryString}`);
            const data = await response.json();
            
            if (data.success) {
                this.beds = data.beds;
                this.renderBedGrid();
                this.updateBedTable();
            }
        } catch (error) {
            console.error('Error applying filters:', error);
        }
    }

    clearFilters() {
        document.getElementById('bedTypeFilter').value = '';
        document.getElementById('statusFilter').value = '';
        document.getElementById('roomFilter').value = '';
        document.getElementById('patientFilter').value = '';
        
        this.loadBeds();
    }

    async addBed() {
        const formData = {
            bed_type: document.getElementById('bedType').value,
            room_number: document.getElementById('roomNumber').value,
            location: document.getElementById('location').value,
            price_per_day: document.getElementById('pricePerDay').value,
            features: []
        };
        
        // Get selected features
        const featureCheckboxes = document.querySelectorAll('input[type="checkbox"]:checked');
        featureCheckboxes.forEach(cb => {
            formData.features.push(cb.value);
        });
        
        if (!formData.bed_type || !formData.room_number) {
            alert('Please fill in all required fields');
            return;
        }
        
        try {
            const response = await fetch('/centre/add-bed', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(formData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert('Bed added successfully!');
                location.reload();
            } else {
                alert(data.message || 'Failed to add bed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to add bed');
        }
    }

    allocateBed(bedId) {
        document.getElementById('selectedBedId').value = bedId;
        document.getElementById('actionType').value = 'allocate';
        const modal = new bootstrap.Modal(document.getElementById('patientSelectModal'));
        modal.show();
    }

    reserveBed(bedId) {
        document.getElementById('selectedBedId').value = bedId;
        document.getElementById('actionType').value = 'reserve';
        const modal = new bootstrap.Modal(document.getElementById('patientSelectModal'));
        modal.show();
    }

    async selectPatient(patientId, patientName) {
        const bedId = document.getElementById('selectedBedId').value;
        const actionType = document.getElementById('actionType').value;
        
        const endpoint = actionType === 'allocate' ? '/centre/allocate-bed' : '/centre/reserve-bed';
        
        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    bed_id: bedId,
                    patient_id: patientId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                alert(data.message);
                location.reload();
            } else {
                alert(data.message || 'Operation failed');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Operation failed');
        }
    }

    async checkoutBed(bedId) {
        if (confirm('Are you sure you want to checkout the patient from this bed?')) {
            try {
                const response = await fetch('/centre/checkout-bed', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ bed_id: bedId })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert(data.message || 'Checkout failed');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Checkout failed');
            }
        }
    }

    async markAvailable(bedId) {
        if (confirm('Mark this bed as available after cleaning?')) {
            try {
                const response = await fetch('/centre/mark-bed-available', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ bed_id: bedId })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert(data.message || 'Failed to mark bed as available');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to mark bed as available');
            }
        }
    }

    async cancelReservation(bedId) {
        if (confirm('Are you sure you want to cancel this reservation?')) {
            try {
                const response = await fetch('/centre/cancel-reservation', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ bed_id: bedId })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    alert(data.message);
                    location.reload();
                } else {
                    alert(data.message || 'Failed to cancel reservation');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Failed to cancel reservation');
            }
        }
    }

    viewBedDetails(bedId) {
        const bed = this.beds.find(b => b.bed_id === bedId);
        if (!bed) return;
        
        const content = `
            <div class="row">
                <div class="col-md-6">
                    <h6>Bed Information</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Bed ID:</strong></td><td>${bed.bed_id}</td></tr>
                        <tr><td><strong>Type:</strong></td><td>${bed.bed_type.replace('_', ' ').toUpperCase()}</td></tr>
                        <tr><td><strong>Room:</strong></td><td>${bed.room_number}</td></tr>
                        <tr><td><strong>Location:</strong></td><td>${bed.location || 'N/A'}</td></tr>
                        <tr><td><strong>Price/Day:</strong></td><td>₹${bed.price_per_day}</td></tr>
                        <tr><td><strong>Status:</strong></td><td><span class="status-badge status-${bed.status}">${bed.status.replace('_', ' ').toUpperCase()}</span></td></tr>
                    </table>
                </div>
                <div class="col-md-6">
                    <h6>Current Occupancy</h6>
                    <table class="table table-sm">
                        <tr><td><strong>Patient:</strong></td><td>${bed.current_patient_name || 'N/A'}</td></tr>
                        <tr><td><strong>Check-in:</strong></td><td>${bed.check_in_date ? new Date(bed.check_in_date).toLocaleDateString() : 'N/A'}</td></tr>
                        <tr><td><strong>Check-out:</strong></td><td>${bed.check_out_date ? new Date(bed.check_out_date).toLocaleDateString() : 'N/A'}</td></tr>
                    </table>
                    ${bed.features && bed.features.length > 0 ? `
                        <h6>Features</h6>
                        <div class="d-flex flex-wrap gap-1">
                            ${bed.features.map(feature => `<span class="badge bg-secondary">${feature.replace('_', ' ').toUpperCase()}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
        
        document.getElementById('bedDetailsContent').innerHTML = content;
        const modal = new bootstrap.Modal(document.getElementById('bedDetailsModal'));
        modal.show();
    }

    searchPatients(searchTerm) {
        const patientItems = document.querySelectorAll('#patientList .list-group-item');
        
        patientItems.forEach(item => {
            const patientName = item.querySelector('h6').textContent.toLowerCase();
            const patientId = item.querySelector('small').textContent.toLowerCase();
            
            if (patientName.includes(searchTerm.toLowerCase()) || patientId.includes(searchTerm.toLowerCase())) {
                item.style.display = 'block';
            } else {
                item.style.display = 'none';
            }
        });
    }

    startAutoRefresh() {
        // Refresh bed data every 30 seconds
        this.refreshInterval = setInterval(() => {
            this.loadBeds();
            this.loadStats();
        }, 30000);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }
}

// Global functions for backward compatibility
let bedManager;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    bedManager = new BedManager();
    
    // Global functions for template compatibility
    window.addBed = () => bedManager.addBed();
    window.allocateBed = (bedId) => bedManager.allocateBed(bedId);
    window.reserveBed = (bedId) => bedManager.reserveBed(bedId);
    window.selectPatient = (patientId, patientName) => bedManager.selectPatient(patientId, patientName);
    window.checkoutBed = (bedId) => bedManager.checkoutBed(bedId);
    window.markAvailable = (bedId) => bedManager.markAvailable(bedId);
    window.cancelReservation = (bedId) => bedManager.cancelReservation(bedId);
    window.viewBedDetails = (bedId) => bedManager.viewBedDetails(bedId);
    window.applyFilters = () => bedManager.applyFilters();
    window.clearFilters = () => bedManager.clearFilters();
});

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (bedManager) {
        bedManager.stopAutoRefresh();
    }
});
