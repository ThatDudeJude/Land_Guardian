// Custom icon creation function
function createCustomIcon(riskLevel, isActive = false) {
    const colors = {
        'low': '#28a745',
        'medium': '#ffc107',
        'high': '#dc3545'
    };

    const size = isActive ? 25 : 20;
    const pulse = isActive ? 'pulse 2s infinite' : 'none';

    return L.divIcon({
        html: `<div style="
            background-color: ${colors[riskLevel]};
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            border: 3px solid white;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
            animation: ${pulse};
        "></div>`,
        className: 'custom-marker',
        iconSize: [size, size],
        iconAnchor: [size/2, size/2]
    });
}

// Global Map Manager Object
window.MapManager = {
    map: null,
    parcelMarkers: {},
    activeParcelId: null,

    init: function(mapInstance) {
        this.map = mapInstance;
    },

    focusOnParcel: function(lat, lng, parcelId) {
        try {
            // Reset previous active marker
            if (this.activeParcelId && this.parcelMarkers[this.activeParcelId]) {
                const prevMarker = this.parcelMarkers[this.activeParcelId];
                const riskLevel = prevMarker.options.riskLevel;
                prevMarker.setIcon(createCustomIcon(riskLevel, false));
            }

            // Fly to location
            this.map.flyTo([lat, lng], 15, { duration: 1.5 });

            // Close other popups
            Object.values(this.parcelMarkers).forEach(marker => {
                marker.closePopup();
            });

            // Animate target marker
            if (this.parcelMarkers[parcelId]) {
                const marker = this.parcelMarkers[parcelId];
                const riskLevel = marker.options.riskLevel;
                marker.setIcon(createCustomIcon(riskLevel, true));

                setTimeout(() => {
                    marker.openPopup();
                }, 1600);
            }

            // Update active state
            this.setActiveParcel(parcelId);
        } catch (error) {
            console.error('Error focusing on parcel:', error);
        }
    },

    setActiveParcel: function(parcelId) {
        // Remove active class from all cards
        document.querySelectorAll('.parcel-card').forEach(card => {
            card.classList.remove('active');
        });

        // Add active class to clicked card
        const activeCard = document.querySelector(`[data-id="${parcelId}"]`);
        if (activeCard) {
            activeCard.classList.add('active');
        }

        this.activeParcelId = parcelId;
    },

    resetMapView: function() {
        try {
            this.map.flyTo([37.7749, -122.4194], 12, { duration: 1 });
            Object.values(this.parcelMarkers).forEach(marker => {
                marker.closePopup();
            });
            this.setActiveParcel(null);
        } catch (error) {
            console.error('Error resetting map view:', error);
        }
    }
};

// Map initialization function
const initMap = (parcels) => {
    try {
        const map = L.map('map').setView([37.7749, -122.4194], 12);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }).addTo(map);

        // Initialize MapManager
        window.MapManager.init(map);

        // Store parcels for keyboard navigation
        window.parcelData = parcels;

        parcels.forEach(parcel => {
            if (parcel.latitude && parcel.longitude) {
                const riskLevel = parcel.risk_level.toLowerCase();
                const marker = createCustomIcon(riskLevel, false);
                const mapMarker = L.marker([parcel.latitude, parcel.longitude], {icon: marker, riskLevel: riskLevel}).addTo(map)
                    .bindPopup(`
                        <div class="text-center">
                            <h6 class="fw-bold">${parcel.name}</h6>
                            <div class="progress mb-2" style="height: 20px;">
                                <div class="progress-bar bg-${riskLevel === 'low' ? 'success' : riskLevel === 'medium' ? 'warning' : 'danger'}" style="width: ${parcel.health_score}%;">
                                    ${parcel.health_score}%
                                </div>
                            </div>
                            <p class="mb-1"><strong>Risk:</strong> <span class="badge bg-${riskLevel === 'low' ? 'success' : riskLevel === 'medium' ? 'warning' : 'danger'}">${parcel.risk_label}</span></p>
                            <p class="mb-2"><small>Soil: ${parcel.soil_quality}/10 • Vegetation: ${parcel.vegetation_cover}/10</small></p>
                            <div class="d-grid gap-1">
                                <a href="/parcel/${parcel.id}" class="btn btn-sm btn-${riskLevel === 'low' ? 'success' : riskLevel === 'medium' ? 'warning' : 'danger'}">View Details</a>
                                <button class="btn btn-sm btn-outline-secondary" onclick="window.MapManager.resetMapView()">Reset Map</button>
                            </div>
                        </div>
                    `);
                window.MapManager.parcelMarkers[parcel.id] = mapMarker;
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