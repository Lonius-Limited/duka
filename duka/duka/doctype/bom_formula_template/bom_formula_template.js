// Copyright (c) 2022, Lonius Devs and contributors
// For license information, please see license.txt

frappe.ui.form.on('BOM Formula Template', {
	// refresh: function(frm) {

	// }
});
frappe.ui.form.on('Bom Template Items', {
	// refresh: function(frm) {

	// }
	items_add:(frm)=>{
		// frappe.msgprint("Adding")
		var items = frm.doc.items.map(row=>row.item_code)
		frm.set_query('item_code', 'items', () => {
			return {
				filters: {
					name: ["NOT IN", items],
					is_stock_item: 1
				}
			}
		})
	}
});