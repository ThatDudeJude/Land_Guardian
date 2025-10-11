// Map initialization function
const initMap = (parcels) => {
    try {
        const map = L.map('map').setView([37.7749, -122.4194], 10);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        parcels.forEach(parcel => {
            if (parcel.latitude && parcel.longitude) {
                const color = parcel.risk_level === 'Low' ? 'green' : parcel.risk_level === 'Medium' ? 'orange' : 'red';
                const marker = L.divIcon({
                    className: 'custom-marker',
                    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white;"></div>`,
                    iconSize: [20, 20],
                    iconAnchor: [10, 10]
                });
                L.marker([parcel.latitude, parcel.longitude], {icon: marker}).addTo(map)
                    .bindPopup(`
                        <strong>${parcel.name}</strong><br>
                        Health Score: ${parcel.health_score}<br>
                        <span class="badge bg-${color === 'green' ? 'success' : color === 'orange' ? 'warning' : 'danger'}">${parcel.risk_label}</span><br>
                        <a href="/parcel/${parcel.id}" class="btn btn-sm btn-primary">View Details</a>
                    `);
            }
        });
    } catch (error) {
        console.error('Error initializing map:', error);
    }
};

// Chart initialization function
const initChart = async (parcelId) => {
    try {
        const response = await fetch(`/api/health-trend/${parcelId}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        const ctx = document.getElementById('healthChart').getContext('2d');
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.map(d => d.date),
                datasets: [{
                    label: 'Health Score',
                    data: data.map(d => d.score),
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error initializing chart:', error);
    }
};

// Form enhancement function
const initFormPreview = () => {
    const soilInput = document.getElementById('soil_quality');
    const vegetationInput = document.getElementById('vegetation_cover');
    const previewElement = document.getElementById('health-preview');

    if (soilInput && vegetationInput && previewElement) {
        const updatePreview = () => {
            const soil = parseFloat(soilInput.value) || 0;
            const vegetation = parseFloat(vegetationInput.value) || 0;
            const healthScore = Math.round((soil * 0.6 + vegetation * 0.4) * 10);
            previewElement.textContent = `Estimated Health Score: ${healthScore}`;
        };

        soilInput.addEventListener('input', updatePreview);
        vegetationInput.addEventListener('input', updatePreview);
    }
};