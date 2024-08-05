// Copyright (c) 2024, Abdul Basit and contributors
// For license information, please see license.txt

frappe.ui.form.on('Price Estimation Tool', {
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