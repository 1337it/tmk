import frappe
import requests
import json
import math
import time
from frappe.utils import now_datetime, get_datetime, add_days, time_diff_in_seconds

TRANSIGHT_URL = "https://compass.transight.in/client/get_vehicle_redis_data/"
HEADERS = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.1 Safari/605.1.15',
    'Referer': 'https://compass.transight.in/client/vehicle/',
    'Cookie': '_ga=GA1.1.245664688.1766585391; _ga_DWD7LPQZRW=GS2.1.s1766585391$o1$g1$t1766585414$j37$l0$h0; csrftoken=Zcn9ETwoFF8fLSf8Qm7Q0d36Lkd7i8MzTJZPmvLX0Ny9vIvcpPg3mRoRgkYjDaao; vlist=added; sessionid=onf2pqnz4q5qldlgypcntapq8xdvl7eb; lang_desc=En_US; language=1',
    'X-Requested-With': 'XMLHttpRequest'
}

def fetch_vehicle_locations_from_api():
    """Fetch latest location from Transight API"""
    # Get all vehicles with tracking ID
    vehicles = frappe.get_all("Vehicle", filters={"custom_tracking_id": ["is", "set"]}, fields=["name", "license_plate", "custom_tracking_id"])
    
    if not vehicles:
        return []

    vehicle_list_payload = [{"veh_id": int(v.custom_tracking_id)} for v in vehicles]
    payload = {
        "vehicle_list": json.dumps(vehicle_list_payload),
        "csrfmiddlewaretoken": "ORUcev8dLtaLzAhVK93nrUR61kUFOCvqIowSW7nM6BAFjqxZjCcANycRwkFR9ETf"
    }

    try:
        response = requests.post(TRANSIGHT_URL, headers=HEADERS, data=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if data.get("status") == "1":
            for item in data.get("data", []):
                # Find matching vehicle in our DB
                veh_db = next((v for v in vehicles if str(v.custom_tracking_id) == str(item["veh_id"])), None)
                if veh_db:
                    lat, lng = item["location"].split(" ")
                    results.append({
                        "vehicle": veh_db.name,
                        "license_plate": veh_db.license_plate,
                        "lat": float(lat),
                        "lng": float(lng),
                        "speed": float(item.get("speed", 0)),
                        "address": item.get("address"),
                        "last_updated": item.get("last_time")
                    })
        return results
    except Exception as e:
        frappe.log_error(f"Transight API Error: {str(e)}", "Transight API")
        return []

def log_vehicle_locations(cached_last_logs=None):
    """Fetch data from API and store in Vehicle GPS Log if criteria met"""
    
    data = fetch_vehicle_locations_from_api()
    if not data:
        return cached_last_logs or {}

    if cached_last_logs is None:
        cached_last_logs = {}
        # Initial load of last log times
        vehicles = frappe.get_all("Vehicle", pluck="name")
        for v in vehicles:
            last_log = frappe.get_all("Vehicle GPS Log", filters={"vehicle": v}, fields=["timestamp"], order_by="timestamp desc", limit=1)
            if last_log:
                cached_last_logs[v] = get_datetime(last_log[0].timestamp)

    now = now_datetime()

    for entry in data:
        vehicle = entry["vehicle"]
        speed = entry["speed"]
        last_log_time = cached_last_logs.get(vehicle)
        
        should_log = False
        
        if last_log_time:
            diff_seconds = time_diff_in_seconds(now, last_log_time)
            if speed > 0:
                # Moving: Log every 10s (approx)
                if diff_seconds >= 10:
                    should_log = True
            else:
                # Stationary: Log every 30s
                if diff_seconds >= 30:
                    should_log = True
        else:
            # First log ever
            should_log = True
            
        if should_log:
            # Create Log Entry
            log = frappe.new_doc("Vehicle GPS Log")
            log.vehicle = entry["vehicle"]
            log.license_plate = entry["license_plate"]
            log.latitude = entry["lat"]
            log.longitude = entry["lng"]
            log.speed = entry["speed"]
            log.address = entry["address"]
            log.timestamp = entry["last_updated"] or now # Use API timestamp if valid, else now
            
            # Create GeoJSON for location field
            log.location = json.dumps({
                "type": "FeatureCollection",
                "features": [{
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [entry["lng"], entry["lat"]]
                    },
                    "properties": {
                        "speed": entry["speed"]
                    }
                }]
            })
            
            log.insert(ignore_permissions=True)
            cached_last_logs[vehicle] = now # Update cache with NOW
    
    # Commit after logging
    frappe.db.commit()
    return cached_last_logs

def run_tracking_loop():
    """Run tracking loop for ~55 seconds to handle sub-minute logging"""
    # Cache to avoid hitting DB for last log time every 10s
    cached_last_logs = None
    
    # Run 6 times (0, 10, 20, 30, 40, 50)
    for i in range(6):
        cached_last_logs = log_vehicle_locations(cached_last_logs)
        if i < 5:
            time.sleep(10)

def get_vehicle_locations():
    """Fetch latest location from DB (Vehicle GPS Log)"""
    vehicles = frappe.get_all("Vehicle", filters={"custom_tracking_id": ["is", "set"]}, pluck="name")
    results = []
    
    for vehicle in vehicles:
        # Get latest log
        logs = frappe.get_all("Vehicle GPS Log", 
            filters={"vehicle": vehicle},
            fields=["vehicle", "license_plate", "latitude", "longitude", "speed", "address", "timestamp"],
            order_by="timestamp desc",
            limit=1
        )
        
        if logs:
            log = logs[0]
            results.append({
                "vehicle": log.vehicle,
                "license_plate": log.license_plate,
                "lat": log.latitude,
                "lng": log.longitude,
                "speed": log.speed,
                "address": log.address,
                "last_updated": log.timestamp
            })
            
    return results

@frappe.whitelist()
def get_trip_details(token):
    """Public API to get trip details for the map"""
    if not frappe.db.exists("Vehicle Trip", token):
         return {"status": "Expired", "message": "Invalid or expired link."}

    trip = frappe.get_doc("Vehicle Trip", token)

    if trip.status != "Active":
        return {"status": trip.status, "message": "This tracking link has expired."}

    # Get current vehicle location from DB
    locations = get_vehicle_locations()
    vehicle_loc = next((l for l in locations if l["vehicle"] == trip.vehicle), None)

    return {
        "status": "Active",
        "vehicle": trip.vehicle,
        "current_location": vehicle_loc,
        "target_location": trip.customer_location,
        "customer": trip.customer,
        "eta": trip.estimated_arrival
    }

def get_distance(lat1, lon1, lat2, lng2):
    """Haversine distance in meters"""
    R = 6371000 # Radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lon1)
    
    a = math.sin(delta_phi / 2)**2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def update_trip_statuses():
    """Scheduled job to check if vehicles reached destination"""
    active_trips = frappe.get_all("Vehicle Trip", filters={"status": "Active"}, fields=["name", "vehicle", "customer_location"])
    if not active_trips:
        return

    locations = get_vehicle_locations()
    if not locations:
        return

    for trip in active_trips:
        if not trip.customer_location:
            continue
            
        # Get vehicle current location
        veh_loc = next((l for l in locations if l["vehicle"] == trip.vehicle), None)
        if not veh_loc:
            continue

        # Parse target location
        try:
            target = json.loads(trip.customer_location)
            # GeoLocation field in frappe can be complex, but usually coordinates are [lng, lat]
            # Handling FeatureCollection or Feature or Geometry
            coords = None
            if "features" in target:
                coords = target["features"][0]["geometry"]["coordinates"]
            elif "geometry" in target:
                coords = target["geometry"]["coordinates"]
            elif "coordinates" in target:
                coords = target["coordinates"]
            
            if coords:
                target_lng, target_lat = coords
                distance = get_distance(veh_loc["lat"], veh_loc["lng"], target_lat, target_lng)
                
                # If within 100 meters, mark as completed
                if distance < 100:
                    frappe.db.set_value("Vehicle Trip", trip.name, {
                        "status": "Completed",
                        "end_time": now_datetime()
                    })
                    frappe.db.commit()
        except:
            continue

def cleanup_gps_logs():
    """Cleanup old logs. Keep 7 days. Keep checkpoints for 6 months."""
    cutoff_date = add_days(now_datetime(), -7)
    checkpoint_cutoff = add_days(now_datetime(), -180) # 6 months

    # 1. Identify checkpoints for logs older than 7 days that haven't been processed
    # We will mark checkpoints for yesterday (or older)
    
    # Get vehicles
    vehicles = frappe.get_all("Vehicle", pluck="name")
    
    for vehicle in vehicles:
        # Find days that need processing (older than 7 days, has logs, not marked)
        # Actually, simpler: Just look at logs > 7 days old that are NOT checkpoints.
        # Select 10 of them per day and mark as checkpoint. Delete the rest.
        
        # This can be heavy. Let's do it simply:
        # Get all logs older than 7 days, is_checkpoint=0
        old_logs = frappe.get_all("Vehicle GPS Log", 
            filters={
                "timestamp": ["<", cutoff_date],
                "is_checkpoint": 0,
                "vehicle": vehicle
            },
            fields=["name", "timestamp", "speed"],
            order_by="timestamp asc"
        )
        
        if not old_logs:
            continue

        # Group by date
        logs_by_date = {}
        for log in old_logs:
            date_str = get_datetime(log.timestamp).strftime("%Y-%m-%d")
            if date_str not in logs_by_date:
                logs_by_date[date_str] = []
            logs_by_date[date_str].append(log)
        
        # For each day, keep max 10
        ids_to_keep = []
        ids_to_delete = []
        
        for date_str, daily_logs in logs_by_date.items():
            # Strategy: Prioritize stopped vehicles (speed < 1), then evenly spaced
            stopped_logs = [l for l in daily_logs if l.speed < 1]
            moving_logs = [l for l in daily_logs if l.speed >= 1]
            
            kept_count = 0
            
            # Keep up to 10 stopped logs (checkpoints)
            for log in stopped_logs[:10]:
                ids_to_keep.append(log.name)
                kept_count += 1
            
            # If we have space, keep some moving logs evenly spaced
            if kept_count < 10 and moving_logs:
                remaining_slots = 10 - kept_count
                step = max(1, len(moving_logs) // remaining_slots)
                for i in range(0, len(moving_logs), step):
                    if kept_count >= 10:
                        break
                    ids_to_keep.append(moving_logs[i].name)
                    kept_count += 1
            
            # Mark the kept ones as checkpoints
            if ids_to_keep:
                frappe.db.sql("UPDATE `tabVehicle GPS Log` SET is_checkpoint=1 WHERE name IN %s", (tuple(ids_to_keep),))
            
            # Delete the rest for this day
            # (Actually we can just delete everything older than 7 days that is NOT a checkpoint)
    
    # 2. Delete all non-checkpoints older than 7 days
    frappe.db.sql("""
        DELETE FROM `tabVehicle GPS Log` 
        WHERE timestamp < %s AND is_checkpoint = 0
    """, (cutoff_date,))
    
    # 3. Delete checkpoints older than 6 months
    frappe.db.sql("""
        DELETE FROM `tabVehicle GPS Log` 
        WHERE timestamp < %s AND is_checkpoint = 1
    """, (checkpoint_cutoff,))
    
    frappe.db.commit()

@frappe.whitelist()
def get_vehicle_status(license_plate):
    """Get status and active trip for a specific vehicle"""
    # Get location
    locations = get_vehicle_locations()
    veh_loc = next((l for l in locations if l["license_plate"] == license_plate), None)
    
    if not veh_loc:
        return None

    # Get active trip
    # Find vehicle name first
    vehicle_doc = frappe.get_value("Vehicle", {"license_plate": license_plate}, "name")
    
    active_trip = frappe.db.get_value("Vehicle Trip", 
        {"vehicle": vehicle_doc, "status": "Active"}, 
        ["name", "customer", "customer_location", "estimated_arrival"], 
        as_dict=1
    )

    return {
        "location": veh_loc,
        "trip": active_trip
    }

@frappe.whitelist()
def get_dashboard_map_data():
    """Get all vehicles location for the dashboard"""
    return get_vehicle_locations()
