frappe.ui.form.on('Purchase Receipt', {
    refresh: (frm) => {
        // if(frm.doc.docstatus==1 && frm.doc.status =="To Bill"){
        if (frm.doc.docstatus == 1 && frm.doc.status == "To Bill") {
            frm.add_custom_button(__("Pay Now (New)"), function () {
                //perform desired action such as routing to new form or fetching etc.
                makeArgs(frm).then(args => submitInvoice(args))
            });
        }
    }

})
const makeArgs = async (frm) => {
    let args = {
        method: "duka.api.purchase_receipt.make_purchase_invoice_shorthand",
        args: {
            docname: frm.doc.name
        },
        freeze: true,
        freeze_message: "Please wait as the liability is posted."
    }
    return args;
}
const submitInvoice = async (args) => {
    frappe.call(args).then(res=>{
        console.log(res)
       
        (!res.message) && frappe.throw("Sorry, an error occured and the transaction did not complete.");

        frappe.set_route(`/app/payment-entry/${res.message}`) 
    })
}