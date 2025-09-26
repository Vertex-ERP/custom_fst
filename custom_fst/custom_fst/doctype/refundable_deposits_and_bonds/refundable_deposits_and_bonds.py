from erpnext.controllers.accounts_controller import AccountsController
import frappe

class RefundableDepositsandBonds(AccountsController):

    def validate(self):
        self.delete_gl_entries()

    def on_change(self):
        gl_entries = []
        self.make_gl_entries(gl_entries)

    def delete_gl_entries(self):
        frappe.db.delete(
            "GL Entry",
            {
                "voucher_type": self.doctype,
                "voucher_no": self.name,
            }
        )
        frappe.db.commit()

    def make_gl_entries(self, gl_entries=None, from_repost=False):
        from erpnext.accounts.general_ledger import make_gl_entries
        if not gl_entries:
            gl_entries = self.get_gl_entries()

        
        make_gl_entries(gl_entries, merge_entries=False, from_repost=from_repost)

    def get_gl_entries(self):
        gl_entries = []
        self.add_bid_bond_gl_entries(gl_entries)
        if self.bond_status == "Released":
            self.receive_bid_bond_gl_entriess(gl_entries)

        return gl_entries

    def receive_bid_bond_gl_entriess(self, gl_entries):
        if self.bond_value and self.bond_value > 0:
            settings = frappe.get_cached_doc('Quotation Settings', 'Quotation Settings')

            if not settings.bid_bond_account or not settings.account or not settings.cost_center:
                frappe.throw(("Quotation Settings is missing required accounts."))

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.bid_bond_account,
                        "debit": self.bond_value,
                        "against": settings.beneficiary_account,
                        "posting_date": self.issuing_date,
                        "company": self.company,
                    }
                )
            )

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.beneficiary_account,
                        "cost_center": settings.cost_center,
                        "credit": self.bond_value,
                        "against": settings.bid_bond_account,
                        "posting_date": self.issuing_date,
                        "company": self.company,
                    }
                )
            )

    # def add_bid_bond_gl_entries(self, gl_entries):
    #         if self.bond_value and self.bond_value > 0:
    #             settings = frappe.get_cached_doc('Quotation Settings', 'Quotation Settings')

    #         if not settings.bid_bond_account or not settings.account or not settings.cost_center:
    #             frappe.throw(("Quotation Settings is missing required accounts."))

    #         gl_entries.append(
    #             self.get_gl_dict(
    #                 {
    #                     "account": settings.bid_bond_account,
    #                     "credit": self.bond_value,
    #                     "against": settings.account,
    #                     "posting_date": self.issuing_date,
    #                     "company": self.company,
    #                 }
    #             )
    #         )

    #         gl_entries.append(
    #             self.get_gl_dict(
    #                 {
    #                     "account": settings.account,
    #                     "cost_center": settings.cost_center,
    #                     "debit": self.bond_value,
    #                     "against": settings.bid_bond_account,
    #                     "posting_date": self.issuing_date,
    #                     "company": self.company,
    #                 }
    #             )
    #         )
    def add_bid_bond_gl_entries(self, gl_entries):
        settings = frappe.get_cached_doc('Quotation Settings', 'Quotation Settings')  # تأكد من تعيينه خارج أي شرط

        if not settings.bid_bond_account or not settings.account or not settings.cost_center:
            frappe.throw(("Quotation Settings is missing required accounts."))

        if self.bond_value and self.bond_value > 0:
            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.bid_bond_account,
                        "credit": self.bond_value,
                        "against": settings.account,
                        "posting_date": self.issuing_date,
                        "company": self.company,
                    }
                )
            )

            gl_entries.append(
                self.get_gl_dict(
                    {
                        "account": settings.account,
                        "cost_center": settings.cost_center,
                        "debit": self.bond_value,
                        "against": settings.bid_bond_account,
                        "posting_date": self.issuing_date,
                        "company": self.company,
                    }
                )
            )
