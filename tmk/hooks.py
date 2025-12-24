app_name = "tmk"
app_title = "TMK Plywood Trading ERP"
app_publisher = "Leet IT Solutions"
app_description = "ERP For TMK"
app_email = "aman@leetitsolutions.com"
app_license = "mit"

# include js in doctype views
doctype_js = {
    "Sales Invoice" : "public/js/sales_common.js",
    "Sales Order" : "public/js/sales_common.js"
}

doc_events = {
	"Sales Invoice": {
		"on_submit": "tmk.whatsapp.send_whatsapp_invoice"
	},
    "Delivery Note": {
        "on_submit": "tmk.whatsapp.send_whatsapp_delivery"
    },
    "Customer": {
        "validate": "tmk.customer.validate_whatsapp_number"
    }
}

export_python_type_annotations = True
