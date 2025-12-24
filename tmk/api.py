import frappe
from frappe import _

@frappe.whitelist()
def get_item_details(customer, item_code):
    if not customer or not item_code:
        return {"customer_history": [], "global_history": [], "stock_a": 0, "stock_b": 0}

    # 1. Last 3 times this item was sold to THIS customer
    customer_history = frappe.db.sql("""
        SELECT sii.rate, sii.qty, si.creation as date
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE si.customer = %s AND sii.item_code = %s AND si.docstatus = 1
        ORDER BY si.creation DESC LIMIT 3
    """, (customer, item_code), as_dict=1)

    # 2. Last 3 times this item was sold to ANY customer
    global_history = frappe.db.sql("""
        SELECT si.customer, sii.rate, sii.qty, si.creation as date
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE sii.item_code = %s AND si.docstatus = 1
        ORDER BY si.creation DESC LIMIT 3
    """, (item_code,), as_dict=1)

    # 3. Stock levels
    wh_a_query = frappe.db.sql("SELECT name FROM tabWarehouse WHERE warehouse_name = 'Warehouse A' LIMIT 1")
    wh_b_query = frappe.db.sql("SELECT name FROM tabWarehouse WHERE warehouse_name = 'Warehouse B' LIMIT 1")
    
    wh_a = wh_a_query[0][0] if wh_a_query else None
    wh_b = wh_b_query[0][0] if wh_b_query else None
    
    stock_a = frappe.db.sql("SELECT actual_qty FROM tabBin WHERE item_code=%s AND warehouse=%s", (item_code, wh_a))[0][0] if wh_a else 0
    stock_b = frappe.db.sql("SELECT actual_qty FROM tabBin WHERE item_code=%s AND warehouse=%s", (item_code, wh_b))[0][0] if wh_b else 0

    return {
        "customer_history": customer_history,
        "global_history": global_history,
        "stock_a": float(stock_a or 0),
        "stock_b": float(stock_b or 0),
        "wh_a_name": wh_a,
        "wh_b_name": wh_b,
        "last_rate": customer_history[0]['rate'] if customer_history else 0
    }

@frappe.whitelist()
def get_customer_history(customer):
    if not customer:
        return []
    return frappe.db.sql("""
        SELECT sii.item_name, sii.rate, sii.parent, si.creation as date
        FROM `tabSales Invoice Item` sii
        JOIN `tabSales Invoice` si ON sii.parent = si.name
        WHERE si.customer = %s AND si.docstatus = 1
        ORDER BY si.creation DESC
        LIMIT 5
    """, (customer,), as_dict=1)
