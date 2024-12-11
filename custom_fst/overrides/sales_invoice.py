from frappe.model.document import Document
import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice,make_regional_gl_entries


class CustomSalesInvoice(SalesInvoice):
    def on_submit(self):
        if self.fst_transfer_stock:
            self.custom_stock_entry_creation()

    def custom_stock_entry_creation(self):
                    source_warehouse = self.get("fst_main_warehouse")
                    target_warehouse = self.get("fst_sub_warehouse")

                    if not source_warehouse or not target_warehouse:
                        frappe.throw("specify the Main Warehouse and the Sub Warehouse.")
                    stock_entry = frappe.new_doc("Stock Entry")
                    stock_entry.stock_entry_type = "Material Transfer"
                    stock_entry.purpose = "Material Transfer"
                    stock_entry.company = self.company

                    for item in self.items:
                        stock_entry.append("items", {
                            "item_code": item.item_code,
                            "qty": item.qty,
                            "uom": item.uom,
                            "stock_uom": item.stock_uom,
                            "conversion_factor": item.conversion_factor,
                            "s_warehouse": source_warehouse,
                            "t_warehouse": target_warehouse,
                        })

                    stock_entry.insert()
                    stock_entry.submit()
@frappe.whitelist()                     
def make_delivery_note(source_name, target_doc=None):

    from frappe.model.mapper import get_mapped_doc

    def update_item(obj, target, source_parent):
        target.fst_ordered_qty = obj.qty
        target.fst_delivered = obj.delivered_qty
        target.fst_remaining_qty = obj.qty - obj.delivered_qty
        target.against_sales_order = obj.sales_order
        target.against_sales_invoice = source_parent.name
        target.si_detail = obj.name
        target.so_detail =obj.so_detail

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
        "Sales Invoice",
        source_name,
        {
            "Sales Invoice": {
                "doctype": "Delivery Note",
                "field_map": {
                    "name": "against_sales_order",
                    "customer": "customer",
                }
            },
            "Sales Invoice Item": {
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
                