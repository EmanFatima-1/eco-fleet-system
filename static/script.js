document.addEventListener('DOMContentLoaded', () => {
    // Initial Data Fetch
    refreshDashboard();

    // Event Listeners
    const vehicleForm = document.getElementById('vehicle-form');
    if (vehicleForm) {
        vehicleForm.addEventListener('submit', handleVehicleRegistration);
    }

    const tripForm = document.getElementById('trip-form');
    if (tripForm) {
        tripForm.addEventListener('submit', handleTripLog);
    }
});

async function refreshDashboard() {
    await Promise.all([
        fetchVehicles(),
        fetchTrips(),
        fetchEmissionsSummary()
    ]);
}

// Fetch all registered vehicles
async function fetchVehicles() {
    try {
        const response = await fetch('/api/vehicles');
        if (!response.ok) throw new Error('Failed to fetch vehicles');
        const vehicles = await response.json();
        
        renderVehiclesTable(vehicles);
        populateVehicleDropdown(vehicles);
        
        const countBadge = document.getElementById('vehicle-count-badge');
        if (countBadge) countBadge.textContent = `${vehicles.length} vehicle${vehicles.length !== 1 ? 's' : ''}`;
        
        const totalVehiclesStat = document.getElementById('stat-total-vehicles');
        if (totalVehiclesStat) totalVehiclesStat.textContent = vehicles.length;
    } catch (err) {
        console.error('Error fetching vehicles:', err);
    }
}

// Render Vehicles Table
function renderVehiclesTable(vehicles) {
    const tbody = document.getElementById('vehicles-table-body');
    if (!tbody) return;

    if (!vehicles || vehicles.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No vehicles registered yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = vehicles.map(v => {
        const typeClass = `type-${(v.vehicle_type || 'default').toLowerCase()}`;
        return `
            <tr>
                <td>#${v.id}</td>
                <td><strong>${escapeHtml(v.name)}</strong></td>
                <td><span class="type-pill ${typeClass}">${escapeHtml(v.vehicle_type)}</span></td>
                <td>${v.fuel_capacity} L/kWh</td>
                <td><span class="badge ${v.is_active ? 'badge-emerald' : ''}">${v.is_active ? 'Active' : 'Inactive'}</span></td>
            </tr>
        `;
    }).join('');
}

// Populate Vehicle Select Dropdown
function populateVehicleDropdown(vehicles) {
    const select = document.getElementById('trip-vehicle-select');
    if (!select) return;

    const currentVal = select.value;
    select.innerHTML = `<option value="" disabled selected>-- Select a Vehicle --</option>`;

    vehicles.forEach(v => {
        const opt = document.createElement('option');
        opt.value = v.id;
        opt.textContent = `#${v.id} - ${v.name} (${v.vehicle_type})`;
        select.appendChild(opt);
    });

    if (currentVal) select.value = currentVal;
}

// Fetch all recorded trips
async function fetchTrips() {
    try {
        const response = await fetch('/api/trips');
        if (!response.ok) throw new Error('Failed to fetch trips');
        const trips = await response.json();

        renderTripsTable(trips);

        // Update stats
        const tripCountBadge = document.getElementById('trip-count-badge');
        if (tripCountBadge) tripCountBadge.textContent = `${trips.length} trip${trips.length !== 1 ? 's' : ''}`;

        const totalTripsStat = document.getElementById('stat-total-trips');
        if (totalTripsStat) totalTripsStat.textContent = trips.length;

        const totalDistance = trips.reduce((acc, t) => acc + (t.distance_km || 0), 0);
        const totalDistanceStat = document.getElementById('stat-total-distance');
        if (totalDistanceStat) totalDistanceStat.textContent = totalDistance.toFixed(1);

    } catch (err) {
        console.error('Error fetching trips:', err);
    }
}

// Render Trips Table
function renderTripsTable(trips) {
    const tbody = document.getElementById('trips-table-body');
    if (!tbody) return;

    if (!trips || trips.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="empty-state">No trip logs recorded yet.</td></tr>`;
        return;
    }

    tbody.innerHTML = trips.map(t => {
        const dateStr = t.timestamp ? new Date(t.timestamp).toLocaleString() : 'N/A';
        const carbonClass = t.carbon_emitted_kg === 0 ? 'text-emerald' : '';
        return `
            <tr>
                <td>#${t.id}</td>
                <td>Vehicle #${t.vehicle_id}</td>
                <td>${t.distance_km} km</td>
                <td>${t.fuel_consumed_liters} L</td>
                <td class="${carbonClass}"><strong>${t.carbon_emitted_kg.toFixed(2)} kg</strong></td>
                <td><small style="color: var(--text-muted);">${dateStr}</small></td>
            </tr>
        `;
    }).join('');
}

// Fetch total carbon emissions summary
async function fetchEmissionsSummary() {
    try {
        const response = await fetch('/api/analytics/emissions');
        if (!response.ok) throw new Error('Failed to fetch emissions');
        const data = await response.json();

        const emissionsStat = document.getElementById('stat-total-emissions');
        if (emissionsStat) {
            const val = Number(data.total_carbon_emitted_kg ?? 0);
            emissionsStat.textContent = isNaN(val) ? '0.00' : val.toFixed(2);
        }
    } catch (err) {
        console.error('Error fetching emissions summary:', err);
    }
}

// Handle Register Vehicle Form Submit
async function handleVehicleRegistration(e) {
    e.preventDefault();
    const btn = document.getElementById('btn-register-vehicle');
    if (btn) btn.disabled = true;

    try {
        const name = document.getElementById('vehicle-name').value.trim();
        const vehicle_type = document.getElementById('vehicle-type').value;
        const fuel_capacity = parseFloat(document.getElementById('fuel-capacity').value);

        const response = await fetch('/api/vehicles', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                vehicle_type,
                fuel_capacity,
                is_active: true
            })
        });

        if (!response.ok) throw new Error('Failed to register vehicle');
        const newVehicle = await response.json();

        showToast(`Vehicle "${newVehicle.name}" registered successfully!`);
        document.getElementById('vehicle-form').reset();
        await refreshDashboard();
    } catch (err) {
        showToast(err.message || 'Error registering vehicle', 'error');
    } finally {
        if (btn) btn.disabled = false;
    }
}

// Handle Record Trip Form Submit
async function handleTripLog(e) {
    e.preventDefault();
    const btn = document.getElementById('btn-record-trip');
    if (btn) btn.disabled = true;

    try {
        const vehicle_id = parseInt(document.getElementById('trip-vehicle-select').value, 10);
        const distance_km = parseFloat(document.getElementById('trip-distance').value);
        const fuel_consumed_liters = parseFloat(document.getElementById('trip-fuel').value);

        if (isNaN(vehicle_id)) {
            throw new Error('Please select a valid vehicle');
        }

        const response = await fetch('/api/trips', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vehicle_id,
                distance_km,
                fuel_consumed_liters
            })
        });

        if (!response.ok) throw new Error('Failed to record trip log');
        const trip = await response.json();

        showToast(`Trip logged! Carbon emitted: ${trip.carbon_emitted_kg} kg CO₂`);
        document.getElementById('trip-form').reset();
        await refreshDashboard();
    } catch (err) {
        showToast(err.message || 'Error recording trip', 'error');
    } finally {
        if (btn) btn.disabled = false;
    }
}

// Toast Helper
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type === 'error' ? 'error' : ''}`;
    toast.textContent = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Escape HTML utility
function escapeHtml(str) {
    return str ? str.replace(/[&<>'"]/g, 
        tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    ) : '';
}
