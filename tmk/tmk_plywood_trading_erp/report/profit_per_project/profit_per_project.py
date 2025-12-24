import frappe
from frappe import _

def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    return columns, data

def get_columns():
    return [
        {"label": _("Project Name"), "fieldname": "project_name", "fieldtype": "Data", "width": 150},
        {"label": _("Sales Amount"), "fieldname": "sales_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Cost Amount"), "fieldname": "cost_amount", "fieldtype": "Currency", "width": 120},
        {"label": _("Profit"), "fieldname": "profit", "fieldtype": "Currency", "width": 120},
        {"label": _("Margin %"), "fieldname": "margin_pct", "fieldtype": "Percent", "width": 100}
    ]

def get_data(filters):
    data = frappe.db.sql("""
        SELECT 
            project_name,
            SUM(base_grand_total) as sales_amount,
            SUM(base_total_taxes_and_charges) as taxes
        FROM `tabSales Invoice`
        WHERE docstatus = 1 AND project_name IS NOT NULL AND project_name != ''
        GROUP BY project_name
    """, as_dict=1)

    # Simplified cost calculation: Fetching incoming rate from Sales Invoice Item
    for row in data:
        costs = frappe.db.sql("""
            SELECT SUM(incoming_rate * qty) 
            FROM `tabSales Invoice Item`
            WHERE parent IN (SELECT name FROM `tabSales Invoice` WHERE project_name = %s AND docstatus = 1)
        """, (row.project_name,))[0][0] or 0
        
        row.cost_amount = costs
        row.profit = row.sales_amount - row.cost_amount
        row.margin_pct = (row.profit / row.sales_amount * 100) if row.sales_amount else 0
        
    return data
