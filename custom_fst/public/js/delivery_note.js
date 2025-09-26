frappe.ui.form.on('Sales Order', {
    refresh: function (frm) {
        // if (frm.doc.docstatus == 1) { 
        //     frm.add_custom_button(__('Sales Invoice'), function () {
        //         frappe.call({
        //             method: "custom_fst.overrides.delivery_note.make_delivery_note1",
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
        // }
    }
});


frappe.ui.form.on('Delivery Note Item', {
    qty: function(frm, cdt, cdn) {
        let obj = frappe.get_doc(cdt, cdn); 
       
        let qty = obj.qty || 0; 
        let fst_delivered = obj.fst_delivered || 0;
         
        let fst_ordered_qty = obj.fst_ordered_qty || 0;

       
        let remaining_qty = fst_ordered_qty- (fst_delivered+qty);

        frappe.model.set_value(cdt, cdn, 'fst_remaining_qty', remaining_qty);
        calculate_total_remaining(frm);
    }
});
function calculate_total_remaining(frm) {
    let total_remaining = 0;

  
    frm.doc.items.forEach(row => {
        total_remaining += row.fst_remaining_qty || 0; 
    });

    frm.set_value('fst_total_remaining', total_remaining);
}
