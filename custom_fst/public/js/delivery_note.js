frappe.ui.form.on('Sales Order', {
    refresh: function (frm) {
        if (frm.doc.docstatus == 1) { 
            frm.add_custom_button(__('Delivery Note'), function () {
                frappe.call({
                    method: "custom_fst.overrides.delivery_note.make_delivery_note",
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
    }
});
