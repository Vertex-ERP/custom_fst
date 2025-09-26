// Copyright (c) 2024, alaalsalam and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Refundable Deposits and Bonds", {
// 	refresh(frm) {

// 	},
// });
frappe.ui.form.on('Refundable Deposits and Bonds', {
    refresh: function(frm) {
        if (frm.doc.bond_status) {
            const indicator_colors = {
                'Updated': 'yellow', 
                'Submitted': 'blue',
                'Expired': 'red',
                'Released': 'purple'
            };

            const color = indicator_colors[frm.doc.bond_status] || 'blue';

            frm.page.set_indicator(__( frm.doc.bond_status), color);
        }
        { 
        frm.events.show_general_ledger(frm);
        erpnext.accounts.ledger_preview.show_accounting_ledger_preview(frm);
        }
    },

    show_general_ledger: function(frm) {
    if (!frm.is_new()) { 
        frm.add_custom_button(
            __("Ledger"),
            function () {
                frappe.route_options = {
                    voucher_no: frm.doc.name,
                    company:frm.doc.company,
                };
                frappe.set_route("query-report", "General Ledger");
            },
            "fa fa-table"
        );
    }
    },
    
    
    });