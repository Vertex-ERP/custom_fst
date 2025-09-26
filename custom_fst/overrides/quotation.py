import frappe

from erpnext.selling.doctype.quotation.quotation import Quotation
from frappe.model.document import Document


from frappe.model.mapper import get_mapped_doc
from erpnext.selling.doctype.quotation.quotation import _make_customer
from frappe.utils import flt, getdate, nowdate,add_days,today


from frappe.utils import flt




from erpnext.accounts.general_ledger import (
    make_gl_entries,
    make_reverse_gl_entries,
    process_gl_map,
)
from erpnext.accounts.utils import (
    create_gain_loss_journal,
    get_account_currency,
    get_currency_precision,
    get_fiscal_years,
    validate_fiscal_year,
)
from frappe.utils import cint, comma_or, flt, getdate, nowdate
from erpnext.accounts.utils import (
    cancel_exchange_gain_loss_journal,
    get_account_currency,
    get_balance_on,
    get_outstanding_invoices,
    get_party_types_from_account_type,
)
from erpnext.accounts.party import get_party_account

from erpnext.accounts.doctype.bank_account.bank_account import (
    get_bank_account_details,
    get_default_company_bank_account,
    get_party_bank_account,
)
from erpnext.accounts.doctype.invoice_discounting.invoice_discounting import (
    get_party_account_based_on_invoice_discounting,
)
from erpnext.controllers.accounts_controller import AccountsController

import frappe
from erpnext.accounts.utils import get_fiscal_year


class CustomQuotation(Quotation):
    

    def on_change(self):
        if self.status == "Lost" and not self.get("custom_make_gl"):
            self.make_gl_entries() 
            self.db_set("custom_make_gl", 1) 


    def make_gl_entries(self, gl_entries=None, from_repost=False):
        from erpnext.accounts.general_ledger import make_gl_entries
        if not gl_entries:
            gl_entries = self.get_gl_entries()

        if gl_entries and self.docstatus == 1:
            make_gl_entries(gl_entries, merge_entries=False, from_repost=from_repost)
        else:
            pass
    
    def get_gl_entries(self):
        gl_entries = []

        
        
        self.add_miscellaneous_expenses_gl_entries(gl_entries)
        self.add_tender_purchase_gl_entries(gl_entries)
        self.add_miscellaneous_expenses2_gl_entries(gl_entries)
        

        

        return gl_entries

    
    def add_miscellaneous_expenses_gl_entries(self, gl_entries):
        if self.miscellaneous_expenses_bid > 0 and self.bid_expences:
            settings = frappe.get_cached_doc('Quotation Settings', 'Quotation Settings')

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.miscellaneous_expenses_bid_account,
                        "credit": self.miscellaneous_expenses_bid,
                        "cost_center": settings.cost_center,
                        "against": settings.account,
                        "posting_date": self.transaction_date,
                    },
                    item=self,
                )
            )

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.account,
                        "cost_center": settings.cost_center,
                        "debit": self.miscellaneous_expenses_bid,
                        "against": settings.miscellaneous_expenses_bid_account,
                        "posting_date": self.transaction_date,
                    },
                    item=self,
                )
            )
    def add_miscellaneous_expenses2_gl_entries(self, gl_entries):
        if self.miscellaneous_expenses > 0 and self.expenses:
            settings = frappe.get_cached_doc('Quotation Settings', 'Quotation Settings')

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.miscellaneous_expenses__account,
                        "credit": self.miscellaneous_expenses,
                        "cost_center": settings.cost_center,
                        "against": settings.account,
                        "posting_date": self.transaction_date,
                    },
                    item=self,
                )
            )

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.account,
                        "cost_center": settings.cost_center,
                        "debit": self.miscellaneous_expenses,
                        "against": settings.miscellaneous_expenses__account,
                        "posting_date": self.transaction_date,
                    },
                    item=self,
                )
            )
    def add_tender_purchase_gl_entries(self, gl_entries):
        if self.buy_value > 0 and self.buy_for_tender_document_:
            settings = frappe.get_cached_doc('Quotation Settings', 'Quotation Settings')

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.buy_value_account,
                        "credit": self.buy_value,
                        "cost_center": settings.cost_center,
                        "against": settings.account,
                        "posting_date": self.transaction_date,
                    },
                    item=self,
                )
            )

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.account,
                        "cost_center": settings.cost_center,
                        "debit": self.buy_value,
                        "against": settings.buy_value_account,
                        "posting_date": self.transaction_date,
                    },
                    item=self,
                )
            )

# في ملف py. الذي يخص Delivery Note

@frappe.whitelist()
def get_sales_order_item_details(item_code, against_sales_order="SAL-ORD-00063"):
    """
    جلب تفاصيل Sales Order Item بناءً على item_code و against_sales_order
    """
    if not (item_code and against_sales_order):
        frappe.msgprint("hi")
        return {}

    sales_order_item = frappe.db.get_value(
        "Sales Order Item",
        {
            "item_code": item_code,
            "parent": against_sales_order  # parent يمثل Sales Order
        },
        ["ordered_qty", "delivered_qty"],
        as_dict=True
    )
    
    return sales_order_item or {}
# custom_fst/overrides/sales_order.py






@frappe.whitelist()
def make_sales_order(source_name: str, target_doc=None):
    # frappe.msgprint("here")
    
    if not frappe.db.get_singles_value(
        "Selling Settings", "allow_sales_order_creation_for_expired_quotation"
    ):
        quotation = frappe.db.get_value(
            "Quotation", source_name, ["transaction_date", "valid_till"], as_dict=1
        )
        if quotation.valid_till and (
            quotation.valid_till < quotation.transaction_date or quotation.valid_till < getdate(nowdate())
        ):
            frappe.throw(_("Validity period of this quotation has ended."))

    return custom_make_sales_order(source_name, target_doc)

def custom_make_sales_order(source_name, target_doc=None, ignore_permissions=False):
    # frappe.msgprint("override")
    customer = _make_customer(source_name, ignore_permissions)
    ordered_items = frappe._dict(
        frappe.db.get_all(
            "Sales Order Item",
            {"prevdoc_docname": source_name, "docstatus": 1},
            ["item_code", "sum(qty)"],
            group_by="item_code",
            as_list=1,
        )
    )

    selected_rows = [x.get("name") for x in frappe.flags.get("args", {}).get("selected_items", [])]

    has_unit_price_items = frappe.db.get_value("Quotation", source_name, "has_unit_price_items")

    def is_unit_price_row(source) -> bool:
        return has_unit_price_items and source.qty == 0

    def set_missing_values(source, target):
        # 👇 your custom mapping
        if source.delivery_:
             target.delivery_date = add_days(today(), int(source.delivery_))

        if customer:
            target.customer = customer.name
            target.customer_name = customer.customer_name

            if not target.get("sales_team"):
                for d in customer.get("sales_team") or []:
                    target.append(
                        "sales_team",
                        {
                            "sales_person": d.sales_person,
                            "allocated_percentage": d.allocated_percentage or None,
                            "commission_rate": d.commission_rate,
                        },
                    )

        if source.referral_sales_partner:
            target.sales_partner = source.referral_sales_partner
            target.commission_rate = frappe.get_value(
                "Sales Partner", source.referral_sales_partner, "commission_rate"
            )

        target.flags.ignore_permissions = ignore_permissions
        target.run_method("set_missing_values")
        target.run_method("calculate_taxes_and_totals")

    def update_item(obj, target, source_parent):
        balance_qty = obj.qty if is_unit_price_row(obj) else obj.qty - ordered_items.get(obj.item_code, 0.0)
        target.qty = balance_qty if balance_qty > 0 else 0
        target.stock_qty = flt(target.qty) * flt(obj.conversion_factor)

        if obj.against_blanket_order:
            target.against_blanket_order = obj.against_blanket_order
            target.blanket_order = obj.blanket_order
            target.blanket_order_rate = obj.blanket_order_rate

    def can_map_row(item) -> bool:
        balance_qty = item.qty - ordered_items.get(item.item_code, 0.0)
        has_valid_qty: bool = (balance_qty > 0) or is_unit_price_row(item)

        if not has_valid_qty:
            return False

        if not selected_rows:
            return not item.is_alternative

        if selected_rows and (item.is_alternative or item.has_alternative_item):
            return item.name in selected_rows

        return True

    doclist = get_mapped_doc(
        "Quotation",
        source_name,
        {
            "Quotation": {
                "doctype": "Sales Order",
                "validation": {"docstatus": ["=", 1]},
                "field_map": {"valid_till": "delivery_date"},  # 👈 extra mapping
            },
            "Quotation Item": {
                "doctype": "Sales Order Item",
                "field_map": {"parent": "prevdoc_docname", "name": "quotation_item"},
                "postprocess": update_item,
                "condition": can_map_row,
            },
            "Sales Taxes and Charges": {"doctype": "Sales Taxes and Charges", "reset_value": True},
            "Sales Team": {"doctype": "Sales Team", "add_if_empty": True},
            "Payment Schedule": {"doctype": "Payment Schedule", "add_if_empty": True},
        },
        target_doc,
        set_missing_values,
        ignore_permissions=ignore_permissions,
    )

    return doclist




