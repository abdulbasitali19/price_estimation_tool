# Copyright (c) 2024, Abdul Basit and contributors
# For license information, please see license.txt

import frappe
import json
from frappe.utils import today
from frappe.model.document import Document
from erpnext.setup.utils import get_exchange_rate

class PriceEstimationTool(Document):

    def validate(self):
        self.items_costing = []
        self.getting_items_with_details()

    def getting_items_with_details(self):
        # Get the current date once
        date = today()
        exchange_rate = get_exchange_rate(self.from_currency,self.to_currency,date)
        if exchange_rate:
            self.exchange_rate = exchange_rate

        # Fetch all item prices in one query for the given price list
        item_prices = frappe.db.get_all("Item Price", filters={"price_list": self.price_list}, fields=["item_code", "price_list_rate"])
        item_prices_dict = {item["item_code"]: item["price_list_rate"] for item in item_prices}
        net = 0
        sum_of_profit = 0

        for item in self.items:
            item_code = item.get("item")
            item_rate_from_price_list = item_prices_dict.get(item_code)

            if item_rate_from_price_list:
                qty = item.get("qty")
                discount = item.get("discount")/100
                exchange_rate = self.exchange_rate
                freight_cost = item.get("freight_cost")
                custom_duty = item.get("custom_duty")
                mis_cost = item.get("mis_cost")
                markup_per = item.get("markup_per")/100
                

                vendor_total_price = item_rate_from_price_list * qty
                vendor_net_price = vendor_total_price * (1 - discount)
                total_extra_cost_per_item = freight_cost + custom_duty + mis_cost
                sub_total = exchange_rate * vendor_net_price
                unit_selling_price_per_item = (sub_total / (1 - markup_per) + total_extra_cost_per_item) / qty
                total_selling_price = unit_selling_price_per_item * qty
                profit = total_selling_price - (sub_total + total_extra_cost_per_item)

                net += total_selling_price
                sum_of_profit += profit
                
                
                self.append("items_costing", {
                    "item": item_code,
                    "vendor_net_price": vendor_net_price,
                    "total_extra_cost": total_extra_cost_per_item,
                    "unit_selling_price": round(unit_selling_price_per_item),
                    "total_selling_price": round(total_selling_price),
                    "profit": round(profit)
                })
                
                
                self.total_selling_price = net
                self.net = net - self.disc
                self.vat15 = self.net * 0.15
                self.total = self.net + self.vat15
                self.total_profit = sum_of_profit
            else:
                frappe.throw(f"{item_code} Rate not Found")
            
@frappe.whitelist()
def create_quotation(doc):
    if not doc:
        frappe.throw("Document is required")
    
    try:
        doc = json.loads(doc)
    except json.JSONDecodeError:
        frappe.throw("Invalid JSON data")

    item_prices = frappe.db.get_all(
        "Item Price",
        filters={"price_list": doc.get("price_list")},
        fields=["item_code", "price_list_rate"]
    )
    
    item_prices_dict = {item["item_code"]: item["price_list_rate"] for item in item_prices}
    
    quotation = frappe.new_doc("Quotation")
    quotation.party_name = doc.get("customer")
    
    quotation_items = []
    for item in doc.get("items", []):
        if item.get("item") in item_prices_dict:
            quotation_items.append({
                "item_code": item.get("item"),
                "qty": item.get("qty"),
                "rate": item_prices_dict[item.get("item")]
            })
        else:
            frappe.msgprint(f"Price for item {item.get('item')} not found in price list {doc.get('price_list')}")
    
    if quotation_items:
        quotation.set("items", quotation_items)
    
    quotation.save(ignore_permissions=True)

    return quotation.name

            
                

