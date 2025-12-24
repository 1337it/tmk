import frappe

def fix_visibility():
    # Clean up duplicate
    if frappe.db.exists("Workspace", "TMK Dashboard"):
        frappe.delete_doc("Workspace", "TMK Dashboard")
        print("Deleted TMK Dashboard")

    # Update TMK Command Center
    if frappe.db.exists("Workspace", "TMK Command Center"):
        frappe.db.set_value("Workspace", "TMK Command Center", {
            "sequence_id": -20,
            "is_hidden": 0,
            "public": 1,
            "icon": "home"
        })
        
        ws = frappe.get_doc("Workspace", "TMK Command Center")
        if not ws.roles:
            ws.append("roles", {"role": "System Manager"})
            ws.append("roles", {"role": "Desk User"})
            ws.save(ignore_permissions=True)
            
        frappe.db.commit()
        print("TMK Command Center updated.")

    frappe.clear_cache()
    print("Cache cleared.")

if __name__ == "__main__":
    fix_visibility()