import frappe


def check():
    frappe.publish_realtime(event='msgprint', message='Hello Socketio', user="Administrator")