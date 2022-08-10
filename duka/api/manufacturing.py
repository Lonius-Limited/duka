import frappe
import json
from frappe import _
from datetime import datetime, date
from frappe.utils import (
	DATE_FORMAT,
	add_days,
	add_to_date,
	cint,
	comma_and,
	date_diff,
	flt,
	getdate,
)


@frappe.whitelist()
# docname, expenses, company, item_name, actual_start_date, cash_or_bank_account
def post_manufacturing_expenses(
	docname, expenses, company, item_name, actual_start_date, cash_or_bank_account=None
):
	# frappe.msgprint("Generating expenses for {company}")
	cash_or_bank = cash_or_bank_account or frappe.get_value(
		"Company", company, "default_cash_account"
	)
	if not cash_or_bank:
		frappe.throw(
			"Sorry, You need to select a cash or bank account for the source of funds to settle this expense."
		)
	payload = json.loads(expenses)
	posting_datetime = datetime.strptime(actual_start_date, "%Y-%m-%d %H:%M:%S.%f")
	actual_posting = posting_datetime.strftime("%Y-%m-%d")
	journal_entry = frappe.new_doc("Journal Entry")
	journal_entry.voucher_type = "Journal Entry"
	link_to_wo = "<a href='{}/app/work-order/{}'>{}</a>".format(
		frappe.utils.get_url(), docname, docname
	)
	journal_entry.user_remark = _(
		"Manufacturing expenses for Work Order {0} for the manufacture of  {1}"
	).format(link_to_wo, item_name)
	journal_entry.company = company
	journal_entry.posting_date = actual_posting
	accounts = make_expense_entries(payload, cash_or_bank, company)
	journal_entry.flags.ignore_permissions = True
	journal_entry.set("accounts", accounts)
	journal_entry.flags.ignore_permissions = True
	journal_entry.save()
	journal_entry.submit()
	journal_html = get_journal_html(accounts,journal_entry.get("user_remark"))
	frappe.db.sql(
		"UPDATE `tabWork Order` SET journal_entry = '{}', journal_html='{}' WHERE name ='{}' ".format(
			journal_entry.get("name"),journal_html, docname
		)
	)
	frappe.msgprint("Expenses have been posted successfully under Voucher ID: <a href='{}/app/journal-entry/{}'>{}</a>".format(
		frappe.utils.get_url(),  journal_entry.get("name"),  journal_entry.get("name")
	), title="Journal Posted Successfully")
	return payload


def make_expense_entries(expenses, cash_or_bank_account, company):
	default_cost_center = frappe.get_value("Company", company, "cost_center")
	precision = frappe.get_precision(
		"Journal Entry Account", "debit_in_account_currency"
	)
	accounts = []

	def _get_expense_accounts(expenses):
		doctype = "Expense Claim Account"
		for x in expenses:
			account = frappe.get_value(
				doctype, dict(parent=x.get("operation")), "default_account"
			)
			x["account"] = account
		return expenses

	e_acc = _get_expense_accounts(expenses)
	distinct_expense_accounts = list(dict.fromkeys(x.get("account") for x in e_acc))
	total_amount = 0.0
	for account in distinct_expense_accounts:
		amt = sum(
			[x.get("operation_cost") for x in e_acc if x.get("account") == account]
		)
		expense_transactions = {
			"account": account,
			"debit_in_account_currency": flt(amt, precision),
			"exchange_rate": flt(1),
			"cost_center": default_cost_center,
		}
		total_amount += amt
		accounts.append(expense_transactions)
	cash_or_bank_transactions = {
		"account": cash_or_bank_account,
		"credit_in_account_currency": flt(total_amount, precision),
		"exchange_rate": flt(1),
		"cost_center": default_cost_center,
	}
	accounts = [cash_or_bank_transactions] + accounts
	return accounts


def get_journal_html(accounts: list, user_remark=None):
	html = """
		<div>
		<em>{}:</em>
		<table class = "table table-responsive table-striped">
		<thead>
		<tr>
		<th>Account</th>
		<th>Debit</th>
		<th>Credit</th>
		</tr>
	</thead><tbody>
		""".format(user_remark or "Manufacturing costs")
	for row in accounts:
		debit = frappe.format(
			row.get("debit_in_account_currency") or 0.0, dict(fieldtype="Currency")
		)
		credit = frappe.format(
			row.get("credit_in_account_currency") or 0.0, dict(fieldtype="Currency")
		)
		html += "<tr><td>{}</td><td>{}</td><td>{}</td></tr>".format(
			row.get("account"), debit, credit
		)
	html += "</tbody><table></div>"
	return html
def test_html_journal():
	jv = "ACC-JV-2022-00003"
	doc = frappe.get_doc("Journal Entry", jv)
	accounts = doc.get("accounts")
	user_remark= doc.get("user_remark")
	jv_html = get_journal_html(accounts,user_remark)
	frappe.db.sql(
		"UPDATE `tabWork Order` SET journal_entry = '{}', journal_html='{}' WHERE name ='{}' ".format(
			jv,jv_html, "MFG-WO-2022-00002"
		)
	)
def work_order_submit(doc, state):
	if not doc.get("expenses"):
		frappe.throw("Please add the expenses incurred in the manufacture of {} under 'Operation Expense' table.".format(doc.get("item_name")))
