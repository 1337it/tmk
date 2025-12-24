import frappe
from frappe.utils import get_url
from frappe import _

def send_whatsapp_invoice(doc, method):
    whatsapp_number = doc.get("whatsapp_number")
    if not whatsapp_number:
        # Try to get from customer
        whatsapp_number = frappe.db.get_value("Customer", doc.customer, "whatsapp_number")
    
    if not whatsapp_number:
        return

    # Generate PDF link
    pdf_url = get_url(f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Invoice&name={doc.name}&format=Standard&no_letterhead=0")
    
    message = f"Hi {doc.customer}, thank you for choosing TMK. Your invoice {doc.name} for ₹{doc.grand_total} is attached. Material is being prepared at Warehouse."
    
    # Placeholder for actual API call
    call_whatsapp_api(whatsapp_number, message, pdf_url)

def send_whatsapp_delivery(doc, method):
    whatsapp_number = doc.get("whatsapp_number")
    if not whatsapp_number:
        whatsapp_number = frappe.db.get_value("Customer", doc.customer, "whatsapp_number")
        
    if not whatsapp_number:
        return

    message = f"Your plywood order {doc.name} is out for delivery from our warehouse."
    call_whatsapp_api(whatsapp_number, message)

def call_whatsapp_api(number, message, media_url=None):
    # This should be replaced with actual integration logic
    frappe.log_error(f"WhatsApp to {number}: {message} (Media: {media_url})", "WhatsApp Notification")