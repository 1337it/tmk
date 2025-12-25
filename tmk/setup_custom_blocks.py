import frappe

def setup_blocks():
    create_block("Vehicle Tracker - KL55V8300", "KL55V8300")
    create_block("Vehicle Tracker - KL-14-E-4593", "KL-14-E-4593")

def create_block(name, license_plate):
    html_content = f'<div id="map-container-{license_plate}" style="height: 400px; width: 100%; border-radius: 8px; border: 1px solid #d1d8dd; position: relative;">Loading Map...</div>'
    
    script_content = get_script(license_plate)

    if not frappe.db.exists("Custom HTML Block", name):
        doc = frappe.new_doc("Custom HTML Block")
        doc.name = name
        doc.html = html_content
        doc.script = script_content
        doc.insert(ignore_permissions=True)
        print(f"Created block {name}")
    else:
        doc = frappe.get_doc("Custom HTML Block", name)
        doc.html = html_content
        doc.script = script_content
        doc.save(ignore_permissions=True)
        print(f"Updated block {name}")

def get_script(license_plate):
    safe_lp = license_plate.replace("-", "").replace(" ", "")
    return f"""
// root_element is available
const container_{safe_lp} = root_element.querySelector("#map-container-{license_plate}");
const lp_{safe_lp} = "{license_plate}";

function loadLeaflet_{safe_lp}(callback) {{
    if (window.L) {{
        callback();
        return;
    }}
    
    if (!document.getElementById('leaflet-css')) {{
        const link = document.createElement('link');
        link.id = 'leaflet-css';
        link.rel = 'stylesheet';
        link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
        document.head.appendChild(link);
    }}
    
    if (!document.getElementById('leaflet-js')) {{
        const script = document.createElement('script');
        script.id = 'leaflet-js';
        script.src = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js';
        script.onload = callback;
        document.head.appendChild(script);
    }} else {{
        // Wait for it
        const check = setInterval(() => {{
            if (window.L) {{
                clearInterval(check);
                callback();
            }}
        }}, 100);
    }}
}}

loadLeaflet_{safe_lp}(() => {{
    if (!container_{safe_lp}) return;
    
    // Cleanup existing map if any (rare in custom block re-render but safe)
    container_{safe_lp}.innerHTML = "";
    
    const map = L.map(container_{safe_lp}).setView([10.85, 76.27], 10);
    L.tileLayer('https://tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
        attribution: '&copy; OpenStreetMap'
    }}).addTo(map);
    
    const icon = L.icon({{
        iconUrl: 'https://cdn-icons-png.flaticon.com/512/741/741407.png',
        iconSize: [32, 32], iconAnchor: [16, 16]
    }});
    
    const update = () => {{
        frappe.call({{
            method: "tmk.tracking.get_vehicle_status",
            args: {{ license_plate: lp_{safe_lp} }},
            callback: (r) => {{
                if (r.message && r.message.location) {{
                    const loc = r.message.location;
                    map.eachLayer(l => {{ if (l instanceof L.Marker) map.removeLayer(l); }});
                    
                    L.marker([loc.lat, loc.lng], {{icon: icon}})
                     .addTo(map)
                     .bindPopup(`<b>${{loc.license_plate}}</b><br>${{loc.speed}} km/h<br>${{loc.address}}`);
                     
                    map.setView([loc.lat, loc.lng], 14);
                }}
            }}
        }});
    }};
    
    update();
    
    // Poll
    const intv = setInterval(() => {{
        if (!document.body.contains(container_{safe_lp})) {{
            clearInterval(intv);
        }} else {{
            update();
        }}
    }}, 10000);
}});
"""

if __name__ == "__main__":
    setup_blocks()
    frappe.db.commit()
