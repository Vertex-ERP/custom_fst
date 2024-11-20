frappe.ui.form.on('Quotation', {
    refresh: function(frm) {
        if (frm.doc.status === "Lost") { 
            frm.events.show_general_ledger(frm);
        erpnext.accounts.ledger_preview.show_accounting_ledger_preview(frm);
        }
    },

    show_general_ledger: function(frm) {
        frm.add_custom_button(
            __("Ledger"),
            function () {
                frappe.route_options = {
                    voucher_no: frm.doc.name,
                };
                frappe.set_route("query-report", "General Ledger");
            },
            "fa fa-table"
        );
    },
    
    });
    
