import frappe
@frappe.whitelist()
def make_delivery_note(source_name, target_doc=None):
    """
    إنشاء Delivery Note من Sales Order مع الحقول المطلوبة.
    """
    from frappe.model.mapper import get_mapped_doc

    def update_item(obj, target, source_parent):
        target.custom_ordered_qty = obj.ordered_qty
        target.custom_delivered_ = obj.delivered_qty 
        target.custom_remaining_qty = obj.ordered_qty - (obj.delivered_qty )
        target.against_sales_order = source_parent.name
        target.so_detail = obj.name

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

    return doc