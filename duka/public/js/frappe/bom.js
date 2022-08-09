// le BOMRESULT = [];
frappe.provide("erpnext.bom");
frappe.ui.form.on('BOM', {
	refresh(frm) {
		// your code here
		console.log("I worked on BOM")
	},
	onload(frm) {
		// frappe.realtime.on("check_bom_progress", function (data) {
		// 	frm.dashboard.show_progress(data.message, (data.count / data.total) * 100, data.message)
		// 	if (data.count == data.total) {
		// 		window.setTimeout( function(message) {frm.dashboard.hide_progress(message)}, 1500, data.messsage)
		// 	}
		// })
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
			let qtyApportioned = (row.percentage_of_total_manufactured_qty * frm.doc.quantity) / 100
			let item = frm.add_child('items', {
				item_code: row.item_code,
				item_name: row.item_name,
				qty: qtyApportioned,
				rate: row.rate,
				base_rate: row.base_rate,
				uom: row.uom,
				stock_uom: row.stock_uom,
				amount: (row.rate || 0.0) * qtyApportioned
			});

		})
		frm.refresh_field('items');
		return frm;
	}
}
const getBomDetails = async (frm, payload) => {
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
				console.log(row, "and", r.message)

				result.push({ ...r.message, ...row })
			},
			freeze: true,
			async: false
		});
	})
	// BOMRESULT = result;
	return result
}
frappe.ui.form.on('Work Order', {
	onload_post_render(frm) {
		if (frm.doc.docstatus == 1 && (frm.doc.journal_entry === null || frm.doc.journal_entry === "" || frm.doc.journal_entry === undefined)) {
			frm.add_custom_button(__("Post Manufacturing Expenses"), function () {
				console.log(frm.doc.expenses.length)
				if (!frm.doc.actual_start_date || parseFloat(frm.doc.produced_qty) < 1) {
					frappe.throw("Sorry, you cannot post expenses for a work order that is not completed yet.")
				}

				if (frm.doc.expenses.length === 0) {
					frappe.msgprint("No expenses have been added on the expenses table so this operation cannot proceed.")
				} else {
					frappe.confirm('Are you sure you want to proceed? You can only post expenses once.',
						() => {
							selectCashOrBank(frm);
						}, () => {
							frappe.show_alert({
								message: __('Action has been cancelled.'),
								indicator: 'green'
							}, 5);
						})

				}
			});
		}
		if (frm.doc.journal_html) {
			frm.set_intro(frm.doc.journal_html, 'blue');
		}

	}
})
frappe.ui.form.on('Work Order Expense', {
	onload(frm) {
		console.log("Loaded on Work Order")
	},
	expenses_add(frm, cdt, cdn) {
		const row = locals[cdt][cdn];
		row.uom = frm.doc.uom

		refresh_field("expenses")
	}
})

const postManufacturingExpenses = async (frm, cash_or_bank_account) => {
	let res = {}
	const docname = frm.doc.name
	let expensesTbl = frm.doc.expenses
	const company = frm.doc.company
	const item_name = frm.doc.item_name
	const actual_start_date = frm.doc.actual_start_date
	const expenses = expensesTbl.map(row => {
		const operation = row.operation;
		const quantity_of_finished_goods = row.quantity_of_finished_goods;
		const uom = row.uom;
		const operation_cost = parseFloat(frm.doc.produced_qty) * parseFloat(row.operation_cost) / parseFloat(quantity_of_finished_goods);
		return {
			operation, quantity_of_finished_goods, uom, operation_cost
		}
	})
	const allArgs = { docname, expenses, company, item_name, actual_start_date, cash_or_bank_account }

	console.log(allArgs)
	const manufacturingArgs = {
		method: "duka.api.manufacturing.post_manufacturing_expenses",
		args: allArgs,
		async: false
	}
	frappe.call(manufacturingArgs).then(response => res = response)
	frm.reload_doc();
	return res
}

const selectCashOrBank = (frm) => {
	let d = new frappe.ui.Dialog({
		title: 'Enter a preferred cash or bank account.',
		fields: [
			{
				fieldname: 'disclaimer',
				fieldtype: 'HTML',
				options:"<h4 style='color:blue'>Select the cash or bank account to be used to settle the expense</h4><em>If you do not select any, system will pick the default cash account in Company settings.</em><hr>"	
			},
			{
				label: 'Default Cash or Bank(Optional)',
				fieldname: 'default_cash_or_bank',
				fieldtype: 'Link',
				options: 'Account',
				get_query: () => {
					return {
						filters: {
							account_type: ["IN", ["Bank", "Cash"]],
							is_group: 0,
							company: frm.doc.company
						}
					};
				},
			}

		],
		primary_action_label: 'Submit',
		primary_action(values) {
			console.log(values);
			const selectedCashOrBankAccount = values.default_cash_or_bank
			postManufacturingExpenses(frm, selectedCashOrBankAccount).then(r => console.log(r))
			d.hide();
		}
	});

	d.show();
}