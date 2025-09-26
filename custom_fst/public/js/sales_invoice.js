frappe.ui.form.on('Sales Invoice', {
    refresh: function (frm) {
        // if (frm.doc.docstatus == 1) { 
        //     frm.add_custom_button(__('Delivery'), function () {
        //         frappe.call({
        //             method: "custom_fst.overrides.sales_invoice.make_delivery_note",
        //             args: {
        //                 source_name: frm.doc.name
        //             },
        //             callback: function (r) {
        //                 if (r.message) {
        //                     frappe.model.sync(r.message);
        //                     frappe.set_route("Form", r.message.doctype, r.message.name);
        //                 }
        //             }
        //         });
        //     }, __('Create'));
     
        if (frm.doc.docstatus == 1) { 
            frm.add_custom_button(__('Stock Entry'), function () {
                frappe.call({
                    method: "custom_fst.overrides.sales_invoice.make_stock_entry",
                    args: {
                        source_name: frm.doc.name
                    },
                    callback: function (r) {
                        if (r.message) {
                            frappe.model.sync(r.message);
                            frappe.set_route("Form", r.message.doctype, r.message.name);
                        }
                    }
                });
            }, __('Create'));
        }
    

     } ,
    fst_transfer_stock: function(frm) {
        if (frm.doc.fst_transfer_stock) {
            frm.set_value('update_stock', 0);
            frm.set_df_property('update_stock', 'hidden', 1);
        } else {
            frm.set_df_property('update_stock', 'hidden', 0);
        }
    }
});
