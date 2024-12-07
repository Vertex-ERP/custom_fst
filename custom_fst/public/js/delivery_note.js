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



// frappe.ui.form.on('Delivery Note', {
//     // تحديث عند تغيير أي شيء في جدول items
//     items_add: function(frm) {
//         calculate_total_remaining_qty(frm);
//     },
//     items_remove: function(frm) {
//         calculate_total_remaining_qty(frm);
//     },
//     validate: function(frm) {
//         calculate_total_remaining_qty(frm);
//     }
// });

// frappe.ui.form.on('Delivery Note Item', {
//     custom_remaining_qty: function(frm, cdt, cdn) {
//         calculate_total_remaining_qty(frm);
//     },
//     item_code: function(frm, cdt, cdn) {
//         calculate_total_remaining_qty(frm);
//         custom_total_ordered_(frm);
//     },
//     custom_ordered_qty:function(frm, cdt, cdn) {
//         custom_total_ordered_(frm);
//     },
// });

// function calculate_total_remaining_qty(frm) {
//     let total = 0;
//     // التكرار على جدول العناصر لجمع القيم
//     frm.doc.items.forEach(item => {
//         total += item.custom_remaining_qty || 0; // إذا كانت القيمة فارغة يتم اعتبارها صفر
//     });
//     frm.set_value('custom_total_remaining_', total); // تعيين القيمة
// }
// function custom_total_ordered_(frm) {
//     let total = 0;
//     // التكرار على جدول العناصر لجمع القيم
//     frm.doc.items.forEach(item => {
//         total += item.custom_ordered_qty || 0; // إذا كانت القيمة فارغة يتم اعتبارها صفر
//     });
//     frm.set_value('custom_total_ordered_', total); // تعيين القيمة
// }
