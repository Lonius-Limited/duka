// le BOMRESULT = [];
frappe.provide("erpnext.bom");
frappe.ui.form.on('BOM', {
	refresh(frm) {
		// your code here
		console.log("I worked on BOM")
	},
	quantity(frm) {
		if (frm.doc.bom_template && frm.doc.items) {
			frm.trigger('bom_template');
		}
	},
	bom_template(frm) {
		if (!frm.doc.bom_template) {
			frappe.msgprint('No formula is selected, transaction will not proceed', 'No Formula Selected')
			return
		}
		frappe.call({
			method: "duka.get_bom_raw_materials",
			args: {
				formula: frm.doc.bom_template
			},
			freeze: true
		}).then(res => {
			console.log(res)
			getBomDetails(frm, res.message).then((bomResult) => {
				resetTable(frm, bomResult)
				
			})

		})
	}
})

const resetTable = async (frm, payload) => {
	if (payload) {
		frm.doc.items = [];
		payload.map(row => {
			let qtyApportioned = (row.percentage_of_total_manufactured_qty * frm.doc.quantity)/100
			let item = frm.add_child('items', {
				item_code: row.item_code,
				item_name: row.item_name,
				qty: qtyApportioned,
				rate:row.rate,
				base_rate: row.base_rate,
				uom: row.uom,
				stock_uom: row.stock_uom,
				amount: (row.rate || 0.0 )*qtyApportioned
			});

		})
		frm.refresh_field('items');
		return frm;
	}
}
const getBomDetails = async(frm, payload) => {
	let result = [];
	payload.map(row => {
		var d = row//locals[cdt][cdn];
		frappe.call({
			doc: frm.doc,
			method: "get_bom_material_detail",
			args: {
				"company": frm.doc.company,
				"item_code": d.item_code,
				"bom_no": d.bom_no != null ? d.bom_no : '',
				"scrap_items": false,
				"qty": d.qty,
				"stock_qty": d.stock_qty,
				"include_item_in_manufacturing": d.include_item_in_manufacturing,
				"uom": d.uom,
				"stock_uom": d.stock_uom,
				"conversion_factor": d.conversion_factor,
				"sourced_by_supplier": d.sourced_by_supplier
			},
			callback: function (r) {
				console.log(row,"and",r.message)

				result.push({...r.message,...row})
			},
			freeze: true,
			async: false
		});
	})
	// BOMRESULT = result;
	return result
}