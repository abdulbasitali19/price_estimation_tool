# Copyright (c) 2024, Abdul Basit and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PriceEstimationTool(Document):
    
    def validate(self):
        if self.items:
            for items in self.items:
                item_rate_from_price_list = frappe.db.get_value("Item Price", {"price_list":self.price_list,"item_code":items.get("item")},"price_list_rate")
                if item_rate_from_price_list:
                    frappe.msgprint(item_rate_from_price_list)
			


# Formula for vendor net price
	# vendor total price =  qty * vendor list price
	#vendor total price( one - dic./comm.)