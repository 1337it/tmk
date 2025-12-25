
frappe.provide('frappe.dashboards.chart_sources');

frappe.dashboards.chart_sources["Vehicle Position"] = {
    method: "tmk.tmk_plywood_trading_erp.dashboard_chart_source.vehicle_position.vehicle_position.execute",
    setup: function(chart, data) {
        console.log("Vehicle Position Chart Setup", data);
        
        // Find the container. chart.parent might be the wrapper, we need to be careful.
        let container = chart.parent;
        if (container.length === 0) {
             console.error("Vehicle Position: Container not found");
             return;
        }
        
        // Clear previous content
        container.empty();
        container.css('min-height', '400px');
        container.css('height', '400px');
        container.css('width', '100%');
        container.css('display', 'block');
        
        const mapId = 'dashboard-map-' + Math.random().toString(36).substr(2, 9);
        $(`<div id="${mapId}" style="width:100%; height:100%;"></div>`).appendTo(container);

        // Extract vehicles
        // Data comes as { labels: [], datasets: [{ values: [1,1], real_data: [...] }] }
        const vehicles = (data && data.datasets && data.datasets[0]) ? data.datasets[0].real_data : [];
        console.log("Vehicles to map:", vehicles);

        // Load Leaflet
        if (!window.L) {
             console.log("Loading Leaflet...");
             $('<link>').appendTo('head').attr({type: 'text/css', rel: 'stylesheet', href: 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css'});
             $.getScript('https://unpkg.com/leaflet@1.9.4/dist/leaflet.js', function() {
                 console.log("Leaflet Loaded.");
                 setTimeout(() => initMap(mapId, vehicles), 100); // Small delay to ensure CSS renders
             });
        } else {
            console.log("Leaflet already loaded.");
            initMap(mapId, vehicles);
        }
    }
};

function initMap(mapId, vehicles) {
    const element = document.getElementById(mapId);
    if (!element) {
        console.error("Map element not found:", mapId);
        return;
    }

    try {
        const map = L.map(mapId).setView([10.8505, 76.2711], 9);
        L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; OpenStreetMap'
        }).addTo(map);
        
        const vehicleIcon = L.icon({
                iconUrl: 'https://cdn-icons-png.flaticon.com/512/741/741407.png',
                iconSize: [32, 32],
                iconAnchor: [16, 16],
                popupAnchor: [0, -16]
        });

        if (vehicles && vehicles.length) {
            const bounds = [];
            vehicles.forEach(v => {
                if (v.lat && v.lng) {
                    L.marker([v.lat, v.lng], {icon: vehicleIcon})
                     .addTo(map)
                     .bindPopup(`<b>${v.license_plate}</b><br>${v.address}<br>Speed: ${v.speed} km/h`);
                    bounds.push([v.lat, v.lng]);
                }
            });
            if (bounds.length) {
                map.fitBounds(bounds, {padding: [50, 50]});
            }
        }
        
        // Force map resize check
        setTimeout(() => { map.invalidateSize(); }, 500);
        
    } catch (e) {
        console.error("Error initializing map:", e);
    }
}
