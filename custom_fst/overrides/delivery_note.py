import frappe
@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None):
    
    from frappe.model.mapper import get_mapped_doc

    def update_item(obj, target, source_parent):
        target.fst_ordered_qty = obj.ordered_qty
        target.fst_delivered = obj.delivered_qty
        target.fst_remaining_qty = obj.ordered_qty - obj.delivered_qty
        target.against_sales_order = source_parent.name
        target.so_detail = obj.name

    def set_totals(doc):
        
        total_ordered = sum(
            [item.fst_ordered_qty for item in doc.items if item.fst_ordered_qty]
        )
        total_remaining = sum(
            [item.fst_remaining_qty for item in doc.items if item.fst_remaining_qty]
        )
        doc.fst_total_ordered = total_ordered
        doc.fst_total_remaining = total_remaining

    doc = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Delivery Note",
                "field_map": {
                    "name": "against_sales_order",
                    "customer": "customer",
                }
            },
            "Sales Order Item": {
                "doctype": "Delivery Note Item",
                "field_map": {
                    "delivered_qty": "delivered_qty"
                },
                "postprocess": update_item,
            },
        },
        target_doc
    )

    # حساب المجاميع
    set_totals(doc)

    return doc
