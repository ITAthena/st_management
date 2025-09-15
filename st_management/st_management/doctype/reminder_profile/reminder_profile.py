# Copyright (c) 2022, Bhavesh Maheshwari and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ReminderProfile(Document):
    def validate(self):
        stc_rules = frappe.get_all("SchTask Control Table", filters={}, fields=["*"])
        for row in stc_rules:
            frappe.db.set_value(
                "SchTask Control Table",
                row.name,
                "stop_escalation",
                self.stop_escalation,
            )
