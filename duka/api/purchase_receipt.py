from __future__ import unicode_literals
import frappe, json

from frappe import _
from frappe.model.mapper import get_mapped_doc
from frappe.utils import get_url, cint
from frappe.utils.background_jobs import enqueue
from frappe import msgprint
from frappe.model.document import Document
import datetime
from frappe.utils import cint, flt, cstr, now
from datetime import date, datetime
from frappe.model.workflow import get_workflow_name, get_workflow_state_field
from frappe.utils import nowdate, getdate, add_days, add_years, cstr, get_url, get_datetime
from frappe.utils import flt, nowdate, get_url
from erpnext.accounts.doctype.payment_request.payment_request import get_payment_entry
from erpnext.accounts.doctype.payment_entry.payment_entry import (
	get_payment_entry,
	get_company_defaults,
)
from erpnext.accounts.utils import get_account_currency


@frappe.whitelist()
def make_purchase_invoice_shorthand(docname):#Purchase receipt name
	due_date =  add_days(nowdate(), 60)
	# posting_date =  add_days(pr_doc.get("posting_date"), 0)
	# frappe.throw(f"{due_date} {posting_date}")
	from erpnext.stock.doctype.purchase_receipt.purchase_receipt import make_purchase_invoice
	purchase_invoice = make_purchase_invoice(docname)
	# purchase_invoice.run_method("set_missing_values")
	# purchase_invoice.posting_date = date.today()
	# purchase_invoice.posting_time = datetime.now().strftime("%H:%M:%S"),
	# purchase_invoice.bill_date = date.today(),
	#set_posting_time
	purchase_invoice.set('set_posting_time', 0)
	purchase_invoice.set('bill_date',nowdate())
	purchase_invoice.set('posting_date', nowdate())
	purchase_invoice.set("due_date", due_date)
	purchase_invoice.set("payment_schedule", [])
	purchase_invoice.flags.ignore_permissions = True

	# frappe.throw(f"{purchase_invoice.__dict__}")
	
	inc_doc = purchase_invoice.insert() #frappe.db.insert(purchase_invoice)

	inc_doc.submit()
	invoice_name =  purchase_invoice.name
	###

	party_account = inc_doc.credit_to
	party_account_currency = inc_doc.get(
		"party_account_currency"
	) or get_account_currency(party_account)
	if (
		party_account_currency == inc_doc.company_currency
		and party_account_currency != inc_doc.currency
	):
		party_amount = inc_doc.base_grand_total
	else:
		party_amount = inc_doc.grand_total
	bank_amount = inc_doc.grand_total

	###


	pe2 = return_custom_payment_entry(
					inc_doc,
					submit=True,
					party_amount=party_amount,
					bank_amount=bank_amount,
					payment_request_doc=None,
				)
	link_to_pe = "<a href = '{}/app/payment-entry/{}' >{}</a>".format(frappe.utils.get_url(),pe2.name,pe2.name)

	msg = "<h4>A supplier Invoice has been posted to Finance as Invoice: {} for evaluation and payment.</h4><p>Click {} to proceed to payment</h4>".format(inc_doc.name, link_to_pe)

	frappe.msgprint(msg, "Posted for Payment")


	return pe2.name

# def get_linked_invoice(docname)
def return_custom_payment_entry(
	doc, submit=False, party_amount=0.0, bank_amount=0.0, payment_request_doc=None
):  # CONTEXT=INVOICE
	payment_entry = get_payment_entry(
		doc.doctype,
		doc.name,
		party_amount=party_amount,
		bank_account=None,
		bank_amount=bank_amount,
	)
	mails = frappe.utils.split_emails(payment_entry.get("contact_email"))
	processed_email = mails[0] if len(mails)>1 else None
	processed_email = frappe.utils.validate_email_address(processed_email)
	payment_entry.update(
		{
			"reference_no": doc.name,
			"reference_date": nowdate(),
			"remarks": "Payment Entry against {0} {1} via direct pay".format(
				doc.doctype, doc.name
			),
			"contact_email": processed_email,
		}
	)

	if payment_entry.difference_amount:
		company_details = get_company_defaults(doc.company)

		payment_entry.append(
			"deductions",
			{
				"account": company_details.exchange_gain_loss_account,
				"cost_center": company_details.cost_center,
				"amount": payment_entry.difference_amount,
			},
		)

	if submit:
		payment_entry.insert(ignore_permissions=True)
		#payment_entry.submit()

	return payment_entry


	