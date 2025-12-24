import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def setup():
    company = frappe.db.get_single_value("Global Defaults", "default_company")
    if not company:
        company = frappe.db.get_value("Company", {"company_name": "TMK Plywood"}, "name")
    
    if not company:
        # Create TMK Plywood Company
        company_doc = frappe.new_doc("Company")
        company_doc.company_name = "TMK Plywood"
        company_doc.default_currency = "INR"
        company_doc.country = "India"
        company_doc.insert()
        company = company_doc.name
        frappe.db.set_value("Global Defaults", "Global Defaults", "default_company", company)
        frappe.db.commit()
        print(f"Created Company: {company}")

    create_warehouses(company)
    create_tmk_custom_fields()

def create_warehouses(company):
    for wh_name in ["Warehouse A", "Warehouse B"]:
        if not frappe.db.exists("Warehouse", {"warehouse_name": wh_name, "company": company}):
            wh = frappe.new_doc("Warehouse")
            wh.warehouse_name = wh_name
            wh.company = company
            wh.insert()
            frappe.db.commit()
            print(f"Created Warehouse: {wh_name}")
        else:
            print(f"Warehouse {wh_name} already exists.")

def create_tmk_custom_fields():
    custom_fields = {
        "Item": [
            {
                "fieldname": "kerala_hsn_code",
                "label": "Kerala HSN Code",
                "fieldtype": "Data",
                "insert_after": "gst_hsn_code"
            },
            {
                "fieldname": "min_stock_level",
                "label": "Minimum Stock Level",
                "fieldtype": "Float",
                "insert_after": "end_of_life"
            }
        ],
        "Customer": [
            {
                "fieldname": "whatsapp_number",
                "label": "WhatsApp Number",
                "fieldtype": "Data",
                "insert_after": "mobile_no"
            }
        ],
        "Sales Invoice": [
            {
                "fieldname": "project_name",
                "label": "Project Name",
                "fieldtype": "Data",
                "insert_after": "customer"
            },
            {
                "fieldname": "whatsapp_number",
                "label": "WhatsApp Number",
                "fieldtype": "Data",
                "insert_after": "project_name"
            }
        ],
        "Delivery Note": [
            {
                "fieldname": "whatsapp_number",
                "label": "WhatsApp Number",
                "fieldtype": "Data",
                "insert_after": "customer"
            }
        ],
        "Sales Invoice Item": [
            {
                "fieldname": "last_sold_rate",
                "label": "Last Sold Rate",
                "fieldtype": "Currency",
                "read_only": 1,
                "insert_after": "rate"
            }
        ],
        "Sales Order Item": [
            {
                "fieldname": "last_sold_rate",
                "label": "Last Sold Rate",
                "fieldtype": "Currency",
                "read_only": 1,
                "insert_after": "rate"
            }
        ]
    }
    create_custom_fields(custom_fields)
    print("Custom fields created successfully.")
