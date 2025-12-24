import frappe

def setup_reports():
    reports = [
        {
            "report_name": "Profit per Project",
            "ref_doctype": "Sales Invoice",
            "report_type": "Script Report",
            "module": "TMK Plywood Trading ERP"
        },
        {
            "report_name": "Stock Ageing Plywood",
            "ref_doctype": "Item",
            "report_type": "Script Report",
            "module": "TMK Plywood Trading ERP"
        },
        {
            "report_name": "Simplified Customer Ledger",
            "ref_doctype": "Customer",
            "report_type": "Script Report",
            "module": "TMK Plywood Trading ERP"
        }
    ]
    
    for r in reports:
        if not frappe.db.exists("Report", r["report_name"]):
            doc = frappe.new_doc("Report")
            doc.update(r)
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"Created Report: {r['report_name']}")
