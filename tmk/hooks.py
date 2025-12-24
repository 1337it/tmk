app_name = "tmk"
app_title = "TMK Plywood Trading ERP"
app_publisher = "Leet IT Solutions"
app_description = "ERP For TMK"
app_email = "aman@leetitsolutions.com"
app_license = "mit"


app_include_css = [
	"/assets/right_hire/css/tmk.css",
	"/assets/right_hire/css/portal-settings.css"
]

app_include_js = [
	"/assets/right_hire/js/portal-settings.js",
	"/assets/right_hire/js/enter-to-next-and-focus-first.js",
	"/assets/right_hire/js/recent_tracker.js"
]
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
