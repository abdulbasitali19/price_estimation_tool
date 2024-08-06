// Copyright (c) 2024, Abdul Basit and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price Estimation Tool', { 
    
    onload:function(frm){
        frm.doc.items_costing = []
        frm.doc.items = []
    },

    refresh: function(frm){
        if(frm.doc.items_costing.length > 0){
            frm.add_custom_button('Create Quotation', () =>
                frappe.call({
                    method :'price_estimation_tool.price_estimation_tool.doctype.price_estimation_tool.price_estimation_tool.create_quotation',
                    args : {
                        doc : frm.doc
                    },
                    freeze: true,
                    freeze_message: "Creating Quotations",
                    callback: function(r) {
                        if(r){
                            frappe.msgprint("quotation created")
                            r = r.message
                            console.log(r)
                        }
                    }
                }) 
            
            )
        }
    },
    
    item: function(frm) {
        update_child_table(frm);
    }
});

    

function update_child_table(frm) {
    let selected_items = frm.doc.item || [];
    let child_table = frm.doc.items || [];

    
    let selected_set = new Set(selected_items);

   
    frm.doc.items = child_table.filter(child_row => selected_set.has(child_row.item));
   
    selected_items.forEach(item_code => {
		
        if (!frm.doc.items.some(child_row => child_row.item === item_code)) {
            let new_child = frm.add_child('items');
            new_child.item = item_code.item;
        }
    });

    frm.refresh_field('items');
}