import frappe
import json
@frappe.whitelist()
def post_manufacturing_expenses(docname):
    payload = frappe.get_all("Work Order Expense", filters=dict(parent =docname),fields =["*"])
    frappe.msgprint(f"{payload}")
    return payload