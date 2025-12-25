import frappe

def create_gps_log_doctype():
    if not frappe.db.exists("DocType", "Vehicle GPS Log"):
        doc = frappe.new_doc("DocType")
        doc.name = "Vehicle GPS Log"
        doc.module = "TMK Plywood Trading ERP"
        doc.custom = 1
        doc.is_submittable = 0
        doc.naming_rule = "Random"
        doc.autoname = "hash"
        
        fields = [
            {"fieldname": "vehicle", "fieldtype": "Link", "options": "Vehicle", "label": "Vehicle", "reqd": 1, "in_list_view": 1},
            {"fieldname": "license_plate", "fieldtype": "Data", "label": "License Plate", "read_only": 1, "in_list_view": 1},
            {"fieldname": "latitude", "fieldtype": "Float", "label": "Latitude", "reqd": 1, "precision": 6},
            {"fieldname": "longitude", "fieldtype": "Float", "label": "Longitude", "reqd": 1, "precision": 6},
            {"fieldname": "location", "fieldtype": "Geolocation", "label": "Location"},
            {"fieldname": "speed", "fieldtype": "Float", "label": "Speed (km/h)"},
            {"fieldname": "address", "fieldtype": "Small Text", "label": "Address"},
            {"fieldname": "timestamp", "fieldtype": "Datetime", "label": "Timestamp", "reqd": 1, "in_list_view": 1},
            {"fieldname": "is_checkpoint", "fieldtype": "Check", "label": "Is Checkpoint", "default": "0"}
        ]
        
        for field in fields:
            doc.append("fields", field)

        doc.append("permissions", {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1})
        doc.append("permissions", {"role": "All", "read": 1})
        
        doc.insert(ignore_permissions=True)
        print("Created Vehicle GPS Log DocType")
    else:
        print("Vehicle GPS Log DocType already exists")

if __name__ == "__main__":
    create_gps_log_doctype()
    frappe.db.commit()
