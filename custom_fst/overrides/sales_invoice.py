from frappe.model.document import Document
import frappe
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice,make_regional_gl_entries
from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice


class CustomSalesInvoices(SalesInvoice):
    def on_submit(self):
        # frappe.msgprint("no ")   

      super(CustomSalesInvoices, self).on_submit()
      if self.fst_transfer_stock:
            self.custom_stock_entry_creation()
            
        
    def custom_stock_entry_creation(self):
        source_warehouse = self.get("fst_main_warehouse")
        target_warehouse = self.get("fst_sub_warehouse")

        if not source_warehouse or not target_warehouse:
            frappe.throw("Please specify both Main Warehouse and Sub Warehouse before proceeding.")

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
                "voucher_type": "Sales Invoice", 
                "voucher_no": self.name  
            })

        stock_entry.insert()
        stock_entry.submit()

        # from erpnext.stock.stock_ledger import make_sl_entries

        # sl_entries = []
        # for item in stock_entry.items:
        #     sl_entries.append(frappe._dict({
        #         "item_code": item.item_code,
        #         "warehouse": source_warehouse,
        #         "posting_date": stock_entry.posting_date,
        #         "posting_time": stock_entry.posting_time,
        #         "voucher_type": "Sales Invoice",
                  
        #         "voucher_no": self.name, 
               
        #         "actual_qty": -item.qty,
        #         "company": self.company,
        #     }))

        #     sl_entries.append(frappe._dict({
        #         "item_code": item.item_code,
        #         "warehouse": target_warehouse,
        #         "posting_date": stock_entry.posting_date,
        #         "posting_time": stock_entry.posting_time,
        #         "voucher_type": "Sales Invoice",  
        #         "voucher_no": self.name, 
        #         "actual_qty": item.qty,
        #         "company": self.company,
        #     }))

        # make_sl_entries(sl_entries, allow_negative_stock=frappe.db.get_value("Stock Settings", None, "allow_negative_stock"))




    # return doc
    
import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_stock_entry(source_name):
    def set_missing_values(source, target):
        target.stock_entry_type = "Material Issue"
        target.company = source.company
        source_warehouse = source.fst_sub_warehouse 
        total_qty = 0  
        for target_item in target.items:
            target_item.s_warehouse = source_warehouse
            # target_item.custom_remains_qty = 
            total_qty += target_item.qty
        target.fst_custom_total_qty = total_qty    
        target.fst_custom_total_order_qty = total_qty    
    stock_entry = get_mapped_doc(
        "Sales Invoice",
        source_name,
        {
            "Sales Invoice": {
                "doctype": "Stock Entry",
                "field_map": {
                    "name": "custom_sales_invoice_reference",
                }
            },
            "Sales Invoice Item": {
                "doctype": "Stock Entry Detail",
                "field_map": {
                    "item_code": "item_code",
                    "qty": "qty",
                    "qty": "fst_custom_order_qty",
                    "uom": "uom",
                    "rate": "basic_rate"
                }
            },
        },
        target_doc=None,
        postprocess=set_missing_values
    )

    
    return stock_entry



# @frappe.whitelist()                     
# def make_delivery_note(source_name, target_doc=None):

    # from frappe.model.mapper import get_mapped_doc

    # def update_item(obj, target, source_parent):
    #     target.fst_ordered_qty = obj.fst_custom_order_qty

    #     target.fst_delivered = obj.delivered_qty
    #     target.fst_remaining_qty = obj.qty -( obj.delivered_qty+obj.qty)
    #     target.against_sales_order = obj.sales_order
    #     target.against_sales_invoice = source_parent.name
    #     target.si_detail = obj.name
    #     target.so_detail =obj.so_detail

    # def set_totals(doc):
        
    #     total_ordered = sum(
    #         [item.fst_ordered_qty for item in doc.items if item.fst_ordered_qty]
    #     )
    #     total_remaining = sum(
    #         [item.fst_remaining_qty for item in doc.items if item.fst_remaining_qty]
    #     )
    #     doc.fst_total_ordered = total_ordered
    #     doc.fst_total_remaining = total_remaining

    # doc = get_mapped_doc(
    #     "Sales Invoice",
    #     source_name,
    #     {
    #         "Sales Invoice": {
    #             "doctype": "Delivery Note",
    #             "field_map": {
    #                 "name": "against_sales_order",
    #                 "customer": "customer",
    #             }
    #         },
    #         "Sales Invoice Item": {
    #             "doctype": "Delivery Note Item",
    #             "field_map": {
    #                 "delivered_qty": "delivered_qty"
    #             },
    #             "postprocess": update_item,
    #         },
    #     },
    #     target_doc
    # )

    # set_totals(doc)