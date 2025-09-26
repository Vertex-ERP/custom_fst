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
import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_stock_entry(source_name):
    def set_missing_values(source, target):
        target.purpose = "Material Issue"
        target.company = source.company

    stock_entry = get_mapped_doc(
        "Sales Invoice",
        source_name,
        {
            "Sales Invoice": {
                "doctype": "Stock Entry",
                "field_map": {
                    "name": "sales_invoice_reference",
                }
            },
            "Sales Invoice Item": {
                "doctype": "Stock Entry Detail",
                "field_map": {
                    "item_code": "item_code",
                    "qty": "qty",
                    "uom": "uom",
                    "rate": "basic_rate"
                }
            },
        },
        target_doc=None,
        postprocess=set_missing_values
    )

    stock_entry.insert()
    return stock_entry

@frappe.whitelist()
def make_delivery_note1(source_name, target_doc=None):
    from frappe.model.mapper import get_mapped_doc

    def update_item(obj, target, source_parent):
        target.fst_ordered_qty = obj.ordered_qty
        income_account = frappe.db.get_value(
        "Item Default",
        {"parent": obj.item_code, "company": source_parent.company},
        "income_account"
    )
        target.income_account = income_account

    doc = get_mapped_doc(
        "Sales Order",
        source_name,
        {
            "Sales Order": {
                "doctype": "Sales Invoice",  # يجب أن يكون Delivery Note بدلاً من Sales Invoice
                "field_map": {
                    "customer": "customer",
                },
            },
            "Sales Order Item": {
                "doctype": "Sales Invoice Item",  # تغيير إلى Delivery Note Item
                "field_map": {},
                "postprocess": update_item,  # استدعاء الدالة لمعالجة الحقول
            },
        },
        target_doc
    )

    return doc
