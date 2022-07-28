# Copyright (c) 2022, Lonius Devs and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class BOMFormulaTemplate(Document):
	def before_save(self):
		
		total = sum([x.get("percentage_of_total_manufactured_qty") for x in self.get("items")])
		total_2dp = float("{:.2f}".format(total)) 
		if total_2dp != 100.00:
			msg = "<h4>Sorry, the total sum of the portions must equal to 100</h4><p style='color:red'>Entered values total to {} %</p>".format(total_2dp)
			frappe.throw(msg, title="Error Adding up to 100%")

