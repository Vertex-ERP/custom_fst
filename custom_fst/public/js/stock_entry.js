frappe.ui.form.on('Stock Entry', {
    validate: function (frm) {
        calculate_totals(frm);
    }
});

frappe.ui.form.on('Stock Entry Detail', {
    qty: function (frm, cdt, cdn) {
        let row = frappe.get_doc(cdt, cdn);
        if (row.fst_custom_order_qty        ) {
            frappe.model.set_value(cdt, cdn, 'fst_custom_remains_qty', row.fst_custom_order_qty - row.qty);
        }
          calculate_totals(frm);
    }
  
});

function calculate_totals(frm) {
    let total_order_qty = 0;
    let total_remains_qty = 0;
    let total_qty = 0;

    (frm.doc.items || []).forEach(row => {
        total_order_qty += row.fst_custom_order_qty || 0;
        total_remains_qty += row.fst_custom_remains_qty  || 0;
        total_qty += row.qty || 0;
    });

    frm.set_value('fst_custom_total_order_qty', total_order_qty);
    frm.set_value('fst_custom_total_remains_qty', total_remains_qty);
    frm.set_value('fst_custom_total_qty', total_qty);
}