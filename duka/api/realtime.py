import frappe


def check():
    # frappe.publish_realtime('msgprint', message='Hello Socketio')
    # doctype, docname = "User", "cashier@lonius.co.ke"
    # description = "Hello shifty"
    # frappe.publish_progress(10, title=None, doctype=None, docname=None, description=None)
    msg_var= "Hey little baby"
    frappe.publish_realtime(event='eval_js', message='alert("{0}")'.format(msg_var), user="Administrator")
