import frappe
from frappe import _
from frappe.utils import nowdate, days_diff

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Item Code"), "fieldname": "item_code", "fieldtype": "Link", "options": "Item", "width": 150},
        {"label": _("Item Name"), "fieldname": "item_name", "fieldtype": "Data", "width": 200},
        {"label": _("Warehouse"), "fieldname": "warehouse", "fieldtype": "Link", "options": "Warehouse", "width": 150},
        {"label": _("Stock Qty"), "fieldname": "actual_qty", "fieldtype": "Float", "width": 100},
        {"label": _("Last Stock In Date"), "fieldname": "last_in_date", "fieldtype": "Date", "width": 120},
        {"label": _("Age (Days)"), "fieldname": "age_days", "fieldtype": "Int", "width": 100}
    ]

def get_data(filters):
    # Simplified Ageing: Get current stock and the latest Stock Ledger Entry (Inward)
    bins = frappe.db.sql("""
        SELECT 
            b.item_code, 
            i.item_name, 
            b.warehouse, 
            b.actual_qty
        FROM `tabBin` b
        JOIN `tabItem` i ON b.item_code = i.name
        WHERE b.actual_qty > 0
    """, as_dict=1)

    data = []
    today = nowdate()

    for row in bins:
        last_in = frappe.db.get_value("Stock Ledger Entry", 
            {"item_code": row.item_code, "warehouse": row.warehouse, "actual_qty": (">", 0)}, 
            "posting_date", order_by="posting_date desc")
        
        if last_in:
            row.last_in_date = last_in
            row.age_days = days_diff(today, last_in)
            data.append(row)
        else:
            row.last_in_date = None
            row.age_days = 0
            data.append(row)
            
    return data
