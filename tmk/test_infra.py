import frappe

def setup_minimal_erpnext():
    # Fix Warehouse Types
    for wt in ["Stock", "Transit", "Consignment", "Commission Admitted"]:
        if not frappe.db.exists("Warehouse Type", wt):
            doc = frappe.new_doc("Warehouse Type")
            doc.name = wt
            doc.insert(ignore_permissions=True)
            frappe.db.commit()

    # Fix Delivery Zone if missing (to avoid Customer validation error)
    if not frappe.db.exists("DocType", "Delivery Zone"):
        doc = frappe.get_doc({
            "doctype": "DocType",
            "name": "Delivery Zone",
            "module": "Setup",
            "custom": 1,
            "fields": [
                {"fieldname": "delivery_zone", "label": "Delivery Zone", "fieldtype": "Data"}
            ],
            "permissions": [{"role": "System Manager", "read": 1, "write": 1, "create": 1}]
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()