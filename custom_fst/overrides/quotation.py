import frappe

from erpnext.selling.doctype.quotation.quotation import Quotation
from frappe.model.document import Document



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
        if self.status == "Lost" and not self.get("rfq_from_venders_and_evaluation"):
            self.make_gl_entries() 
            self.db_set("rfq_from_venders_and_evaluation", 1) 


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

        
        self.add_bid_bond_gl_entries(gl_entries)
        
        self.add_miscellaneous_expenses_gl_entries(gl_entries)
        self.add_tender_purchase_gl_entries(self)
        

        

        return gl_entries

    def add_bid_bond_gl_entries(self, gl_entries):
        if self.bid_bond_value_tender and self.bid_bond_value_tender > 0:
            settings = frappe.get_cached_doc('Quotation Settings', 'Quotation Settings')

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.bid_bond_account,
                        "debit": self.bid_bond_value_tender,
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
                        "credit": self.bid_bond_value_tender,
                        "against": settings.bid_bond_account,
                        "posting_date": self.transaction_date,
                    },
                    item=self,
                )
            )

    def add_miscellaneous_expenses_gl_entries(self, gl_entries):
        if self.miscellaneous_expenses_bid > 0:
            settings = frappe.get_cached_doc('Quotation Settings', 'Quotation Settings')

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.miscellaneous_expenses_bid_account,
                        "debit": self.miscellaneous_expenses_bid,
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
                        "credit": self.miscellaneous_expenses_bid,
                        "against": settings.miscellaneous_expenses_bid_account,
                        "posting_date": self.transaction_date,
                    },
                    item=self,
                )
            )
    def add_tender_purchase_gl_entries(self, gl_entries):
        if self.buy_value > 0:
            settings = frappe.get_cached_doc('Quotation Settings', 'Quotation Settings')

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.buy_value_account,
                        "debit": self.buy_value,
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
                        "credit": self.buy_value,
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



