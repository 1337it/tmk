app_name = "tmk"
app_title = "TMK Plywood Trading ERP"
app_publisher = "Leet IT Solutions"
app_description = "ERP For TMK"
app_email = "aman@leetitsolutions.com"
app_license = "mit"


app_include_css = [
	"/assets/tmk/css/tmk.css",
	"/assets/tmk/css/portal-settings.css"
]

app_include_js = [
	"/assets/tmk/js/portal-settings.js",
	"/assets/tmk/js/enter-to-next-and-focus-first.js",
	"/assets/tmk/js/recent_tracker.js",
    "/assets/tmk/js/persistent_sidebar.js"
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

scheduler_events = {
    "cron": {
        "* * * * *": [
            "tmk.tracking.run_tracking_loop",
            "tmk.tracking.update_trip_statuses"
        ]
    },
    "daily": [
        "tmk.tracking.cleanup_gps_logs"
    ]
}

export_python_type_annotations = True
