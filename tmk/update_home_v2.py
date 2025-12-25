import frappe
import json

def update_home_workspace():
    try:
        doc = frappe.get_doc("Workspace", "Home")
        content_json = []
        if doc.content:
            try:
                content_json = json.loads(doc.content)
            except:
                content_json = []

        # Remove old blocks
        content_json = [b for b in content_json if "vehicle-tracking-card" not in str(b) and "Vehicle Tracker" not in str(b)]

        # Add new blocks
        new_blocks = [
            {"type": "header", "data": {"text": "Vehicle Tracking", "level": 3, "col": 12}},
            {
                "type": "custom_block", 
                "data": {
                    "custom_block_name": "Vehicle Tracker - KL55V8300",
                    "col": 6
                }
            },
            {
                "type": "custom_block", 
                "data": {
                    "custom_block_name": "Vehicle Tracker - KL-14-E-4593",
                    "col": 6
                }
            }
        ]

        doc.content = json.dumps(new_blocks + content_json)
        doc.save(ignore_permissions=True)
        print("Updated Home Workspace with Custom Blocks.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    update_home_workspace()
    frappe.db.commit()
