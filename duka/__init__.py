
__version__ = '0.0.1'
import frappe
from frappe import _

def execute_duka_workspaces():
    exclusion_list = ('Master Data','Accounting','Stock','Manufacturing','POS Awesome','Buying')
    print(_(exclusion_list))
    frappe.db.sql("DELETE FROM `tabWorkspace` WHERE name NOT IN {}".format(exclusion_list))
    print("Deleted unnecesary workspaces for Duka")

