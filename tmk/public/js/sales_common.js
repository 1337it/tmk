console.log("TMK Sales Common JS Loaded");
frappe.provide('tmk.utils');

if (!tmk.utils._initialized) {
    tmk.utils._initialized = true;

    tmk.utils.setup_sales_history = function(frm) {
        if (frm.doc.customer && !frm.get_button(__('View Customer History'))) {
            frm.add_custom_button(__('View Customer History'), function() {
                tmk.utils.show_customer_history(frm);
            }, __('Actions'));
        }
    };

    tmk.utils.show_customer_history = function(frm) {
        frappe.call({
            method: "tmk.api.get_customer_history",
            args: {
                customer: frm.doc.customer
            },
            callback: function(r) {
                if (r.message && r.message.length > 0) {
                    let html = `
                        <table class="table table-bordered">
                            <thead>
                                <tr>
                                    <th>${__('Item')}</th>
                                    <th>${__('Rate')}</th>
                                    <th>${__('Source Doc')}</th>
                                    <th>${__('Date')}</th>
                                </tr>
                            </thead>
                            <tbody>
                    `;
                    r.message.forEach(row => {
                        html += `
                            <tr>
                                <td>${row.item_name}</td>
                                <td>${frappe.format(row.rate, {fieldtype: 'Currency'})}</td>
                                <td><a href="/app/sales-invoice/${row.parent}">${row.parent}</a></td>
                                <td>${frappe.datetime.global_date_format(row.date)}</td>
                            </tr>
                        `;
                    });
                    html += `</tbody></table>`;
                    
                    frappe.msgprint({
                        title: __('Last 5 Transactions for ' + frm.doc.customer),
                        message: html,
                        wide: true
                    });
                } else {
                    frappe.show_alert(__('No previous transactions found for this customer.'));
                }
            }
        });
    };

    tmk.utils.fetch_item_insights = function(frm, cdt, cdn) {
        try {
            let row = locals[cdt][cdn];
            if (row._fetching_insights) return;
            
            if (row.item_code && frm.doc.customer) {
                row._fetching_insights = true;
                frappe.call({
                    method: "tmk.api.get_item_details",
                    args: {
                        customer: frm.doc.customer,
                        item_code: row.item_code
                    },
                    callback: function(r) {
                        try {
                            if (r.message) {
                                let msg = "";
                                
                                // 1. Customer Specific History
                                msg += `<h5><b>Recent Sales to this Customer:</b></h5>`;
                                if (r.message.customer_history && r.message.customer_history.length > 0) {
                                    msg += `<table class="table table-sm table-bordered">
                                        <thead><tr><th>Date</th><th>Rate</th><th>Qty</th></tr></thead><tbody>`;
                                    r.message.customer_history.forEach(h => {
                                        msg += `<tr>
                                            <td>${frappe.datetime.global_date_format(h.date)}</td>
                                            <td>${frappe.format(h.rate, {fieldtype: 'Currency'})}</td>
                                            <td>${h.qty}</td>
                                        </tr>`;
                                    });
                                    msg += `</tbody></table>`;
                                } else {
                                    msg += `<p>No previous sales to this customer.</p>`;
                                }

                                // 2. Global History
                                msg += `<h5 style="margin-top: 15px;"><b>Recent Sales (Global):</b></h5>`;
                                if (r.message.global_history && r.message.global_history.length > 0) {
                                    msg += `<table class="table table-sm table-bordered">
                                        <thead><tr><th>Customer</th><th>Rate</th><th>Qty</th></tr></thead><tbody>`;
                                    r.message.global_history.forEach(h => {
                                        msg += `<tr>
                                            <td style="font-size: 0.9em">${h.customer}</td>
                                            <td>${frappe.format(h.rate, {fieldtype: 'Currency'})}</td>
                                            <td>${h.qty}</td>
                                        </tr>`;
                                    });
                                    msg += `</tbody></table>`;
                                } else {
                                    msg += `<p>No global sales history found.</p>`;
                                }

                                // 3. Stock
                                msg += `<hr>
                                    <b>Stock A:</b> ${r.message.stock_a} | 
                                    <b>Stock B:</b> ${r.message.stock_b}
                                `;

                                frappe.msgprint({
                                    title: __('Item Insights: ' + row.item_code),
                                    message: msg,
                                    wide: true,
                                    indicator: 'blue'
                                });
                                
                                if (frappe.meta.has_field(cdt, 'last_sold_rate')) {
                                    frappe.model.set_value(cdt, cdn, 'last_sold_rate', r.message.last_rate);
                                }
                            }
                        } finally {
                            row._fetching_insights = false;
                        }
                    }
                });
            }
        } catch (e) {
            console.error("Error in fetch_item_insights:", e);
        }
    };

    let sales_handler = {
        onload: function(frm) { tmk.utils.setup_sales_history(frm); },
        refresh: function(frm) { tmk.utils.setup_sales_history(frm); },
        customer: function(frm) { if (frm.doc.customer) tmk.utils.show_customer_history(frm); }
    };

    let item_handler = {
        item_code: function(frm, cdt, cdn) { tmk.utils.fetch_item_insights(frm, cdt, cdn); }
    };

    frappe.ui.form.on('Sales Invoice', sales_handler);
    frappe.ui.form.on('Sales Invoice Item', item_handler);
    frappe.ui.form.on('Sales Order', sales_handler);
    frappe.ui.form.on('Sales Order Item', item_handler);
}
