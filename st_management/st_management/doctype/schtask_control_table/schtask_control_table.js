// Copyright (c) 2022, Bhavesh Maheshwari and contributors
// For license information, please see license.txt

frappe.ui.form.on('SchTask Control Table', {
	onload: function (frm) {
		frm.set_query("model", function () {
			return {
				filters: [
					["DocField", "options", "=", "ST Status"],
					["DocType", "name", "not in", ['Todo Items']]
				],
			};
		});
	}
});
