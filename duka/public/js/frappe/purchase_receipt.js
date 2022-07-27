frappe.ui.form.on('Purchase Receipt', {
    refresh: (frm) => {
        // if(frm.doc.docstatus==1 && frm.doc.status =="To Bill"){
        if (frm.doc.docstatus == 1 && frm.doc.status == "To Bill") {
            frm.add_custom_button(__("Pay Now(New)"), function () {
                //perform desired action such as routing to new form or fetching etc.
                makeArgs(frm).then(args => submitInvoice(args))
            });
        }

        // if (frm.doc.docstatus == 1 && frm.doc.status == "Completed") {
        //     frm.add_custom_button(__("Go To Invoice"), function () {
        //         //perform desired action such as routing to new form or fetching etc.
        //         // makeArgs(frm).then(args => submitInvoice(args))
        //         let invoice = "ACC-PINV-2022-00001"
        //         frappe.set_route(`/app/purchase-invoice/${invoice}`)
        //     });
        // }

    }

})
const makeArgs = async (frm) => {
    let args = {
        method: "duka.api.purchase_receipt.make_purchase_invoice_shorthand",
        args: {
            docname: frm.doc.name
        },
        freeze: true,
        freeze_message: "Please wait as the liability is posted"
    }
    return args;
    //const process = await submitInvoice(frm)
}
const submitInvoice = async (args) => {
    frappe.call(args).then(res=>{
        console.log(res)
        frappe.set_route(`/app/payment-entry/${res.message}`)
    })
}