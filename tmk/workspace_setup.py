import frappe
import json

def setup_workspace():
    if not frappe.db.exists("Workspace", "TMK Dashboard"):
        doc = frappe.new_doc("Workspace")
        doc.label = "TMK Dashboard"
        doc.module = "TMK Plywood Trading ERP"
        doc.is_standard = 1
        doc.public = 1
        doc.title = "TMK Command Center"
        
        shortcuts = [
            {"shortcut_name": "Customer", "link_to": "Customer", "label": "Customers", "type": "DocType"},
            {"shortcut_name": "Item", "link_to": "Item", "label": "Items", "type": "DocType"},
            {"shortcut_name": "Sales Invoice", "link_to": "Sales Invoice", "label": "Sales Invoices", "type": "DocType"},
            {"shortcut_name": "Purchase Invoice", "link_to": "Purchase Invoice", "label": "Purchase Invoices", "type": "DocType"},
            {"shortcut_name": "Payment Entry", "link_to": "Payment Entry", "label": "Payment Entries", "type": "DocType"},
            {"shortcut_name": "Stock Balance", "link_to": "Stock Balance", "label": "Stock Summary", "type": "Report"}
        ]
        
        for s in shortcuts:
            doc.append("shortcuts", s)
            
        doc.insert(ignore_permissions=True)
        frappe.db.commit()

def hide_modules():
    modules_to_hide = ["HR", "Payroll", "Manufacturing", "Education", "Healthcare", "Agriculture", "Hospitality", "Lending"]
    for m in modules_to_hide:
        if frappe.db.exists("Module Def", m):
            frappe.db.set_value("Module Def", m, "disabled", 1)
    frappe.db.commit()