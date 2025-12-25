import frappe

def get_context(context):
    trip_id = frappe.form_dict.get("id")
    if not trip_id:
        context.invalid = True
        return

    if not frappe.db.exists("Vehicle Trip", trip_id):
        context.invalid = True
        return

    trip = frappe.get_doc("Vehicle Trip", trip_id)
    if trip.status != "Active":
        context.expired = True
        return

    context.trip = trip
