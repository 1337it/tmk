import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Customer"), "fieldname": "customer", "fieldtype": "Link", "options": "Customer", "width": 200},
        {"label": _("Total Invoiced"), "fieldname": "total_invoiced", "fieldtype": "Currency", "width": 150},
        {"label": _("Total Paid"), "fieldname": "total_paid", "fieldtype": "Currency", "width": 150},
        {"label": _("Outstanding Balance"), "fieldname": "outstanding", "fieldtype": "Currency", "width": 150}
    ]

def get_data(filters):
    return frappe.db.sql("""
        SELECT 
            customer,
            SUM(base_grand_total) as total_invoiced,
            SUM(base_paid_amount) as total_paid,
            SUM(outstanding_amount) as outstanding
        FROM `tabSales Invoice`
        WHERE docstatus = 1
        GROUP BY customer
    """, as_dict=1)
