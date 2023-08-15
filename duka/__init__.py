
__version__ = '0.0.1'
import frappe, json
from frappe import _
from frappe.core.doctype.session_default_settings.session_default_settings import set_session_default_values, get_session_default_values

def execute_duka_workspaces():
    exclusion_list = ('Master Data','Accounting','Stock','Manufacturing','POS Awesome','Buying')
    print(_(exclusion_list))
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name NOT IN {}".format(exclusion_list))
    print("Deleted unnecesary workspaces for Duka")
@frappe.whitelist()
def get_bom_raw_materials(formula):
    filters = dict(parent = formula)
    return frappe.get_all("Bom Template Items", filters=filters, fields =["*"])
def session_defaults_on_login():
    user =frappe.session.user
    default_user_company = get_default_user_company(user)
    
    if not default_user_company: return

    defaults =  get_session_default_values()
    if not defaults:
        defaults = [{"fieldname": "company", "fieldtype": "Link", "options": "Company", "label": "Default Company", "default": "Value Produce"}]
    else:
        defaults = json.loads(defaults)
    
    for d in defaults:
        if d.get('fieldname')=="company":
            d["default"] = default_user_company
    # frappe.msgprint(f"User : {user} Defaults: {defaults}")
    set_session_default_values(defaults)
    return defaults
def get_default_user_company(user):
    args = dict(allow="Company", user=user)
    return frappe.get_value("User Permission",args,"for_value")
