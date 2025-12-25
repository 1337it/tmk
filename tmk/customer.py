import frappe
from frappe import _
import re

def validate_whatsapp_number(doc, method):
    whatsapp_number = doc.get("whatsapp_number")
    if whatsapp_number:
        # Check if it starts with +91 and has 10 digits after
        if not re.match(r"^\+91\d{10}$", whatsapp_number):
            frappe.throw(_("WhatsApp Number must be in format +91XXXXXXXXXX (e.g., +919876543210)"))
