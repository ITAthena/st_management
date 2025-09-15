import frappe
from frappe.utils import today, add_days, now_datetime, getdate, format_date


@frappe.whitelist()
def get_next_calendar_date(
    calendar, date=None, reminder=False, validate=False, st_name=None
):
    date_cond = ""
    if not date:
        date = add_days(today(), -1)
    if not reminder:
        if getdate(date) < getdate(today()):
            date = add_days(today(), -1)
    if date:
        date_cond += f" and date>'{date}'"
    calendar_dates = frappe.db.sql(
        """select date from `tabST Status Details` where parent=%s {0} order by date asc""".format(
            date_cond
        ),
        calendar,
        as_dict=1,
    )
    if len(calendar_dates) >= 1:
        return calendar_dates[0].date
    else:
        if validate:
            st_doc = frappe.get_doc("SchTask Control Table", st_name)
            st_doc.add_comment(
                "Comment",
                "{0}:No future date exists for mention calendar {1}".format(
                    today(), calendar
                ),
            )
            frappe.log_error(
                title="ST Management Cron Error {0}".format(st_name),
                message="{0}:No future date exists for mention calendar {1}".format(
                    today(), calendar
                ),
            )
            return False
        else:
            return date


@frappe.whitelist()
def create_blank_entry(st_doc):
    dd_date = st_doc.dd_date or add_days(today(), -1)
    next_calendar_date = get_next_calendar_date(
        st_doc.calendar, dd_date, validate=True, st_name=st_doc.name
    )
    if next_calendar_date == False:
        return False
    doc = frappe.get_doc(dict(doctype=st_doc.model))
    doc.description = st_doc.description
    doc.calendar = st_doc.calendar
    doc.dd_date = next_calendar_date
    doc.status = "Not Started"
    doc.responsible_position = st_doc.responsible_position
    doc.stct = st_doc.name
    model_doc_meta = frappe.get_meta(st_doc.model, cached=True)
    for field in model_doc_meta.fields:
        if field.fieldtype == "Link" and st_doc.get("reference_item") == field.options:
            doc.set(field.fieldname, st_doc.get("reference_nr"))
        if field.fieldname == "serial_nr":
            doc.set(field.fieldname, st_doc.get("serial_nr"))
    doc.flags.ignore_mandatory = True
    doc.flags.ignore_validate = True
    return doc.insert(ignore_permissions=True)


def create_todo(st_doc, model_doc):
    doc = frappe.get_doc(
        dict(
            doctype="Todo Items",
            model=st_doc.model,
            series=st_doc.series,
            description=st_doc.description,
            position=st_doc.responsible_position,
            escalation_position=st_doc.escalation_position,
            schtask_control_table=st_doc.name,
            model_name=model_doc.name,
            dd_date=model_doc.dd_date,
            status=model_doc.status,
        )
    )
    reminder_details = get_reminder_days(st_doc, model_doc)
    if reminder_details == False:
        return False
    doc.stop_reminders = st_doc.stop_reminders
    doc.stop_escalation = st_doc.stop_escalation
    doc.first_rem_date = reminder_details.get("first_reminder_date")
    doc.final_rem_date = reminder_details.get("final_reminder_date")
    # change to escalation calendar
    escalation_calendar = frappe.db.get_value(
        "Reminder Profile", st_doc.reminder_profile, "escalation_calendar"
    )
    if escalation_calendar:
        escalation_date = get_next_calendar_date(
            escalation_calendar,
            model_doc.dd_date,
            validate=True,
            reminder=True,
            st_name=st_doc.name,
        )
        if escalation_date == False:
            return False
        doc.escalation_date = escalation_date
    doc.insert(ignore_permissions=True)
    return doc


def get_reminder_days(st_doc, model_doc):
    reminder_details = {"first_reminder_date": "", "final_reminder_date": ""}
    reminder_profile_doc = frappe.get_doc("Reminder Profile", st_doc.reminder_profile)
    first_rem_base_days = reminder_profile_doc.get("1st_rem_base_days")
    final_rem_base_days = reminder_profile_doc.get("final_rem_base_days")
    first_reminder_date = get_next_calendar_date(
        reminder_profile_doc.get("1st_rem_calendar"),
        add_days(model_doc.dd_date, -1 * first_rem_base_days),
        validate=True,
        reminder=True,
        st_name=st_doc.name,
    )
    if first_reminder_date == False:
        return False
    final_reminder_date = get_next_calendar_date(
        reminder_profile_doc.get("final_rem_calendar"),
        add_days(model_doc.dd_date, -1 * final_rem_base_days),
        validate=True,
        reminder=True,
        st_name=st_doc.name,
    )
    if final_reminder_date == False:
        return False
    reminder_details["first_reminder_date"] = first_reminder_date
    reminder_details["final_reminder_date"] = final_reminder_date
    return reminder_details


def update_stct(st_doc, todo_doc):
    next_dd_date = get_next_calendar_date(st_doc.calendar, st_doc.dd_date)
    frappe.db.set_value("SchTask Control Table", st_doc.name, "dd_date", next_dd_date)
    frappe.db.set_value(
        "SchTask Control Table", st_doc.name, "todoitem_nr", todo_doc.name
    )


def cron_st():
    filters = [
        ["dd_date", "<", today()],
        ["dd_date", "is", "not set"],
    ]
    filters = [["disable_task", "=", 0]]
    st_list = frappe.get_all(
        "SchTask Control Table", or_filters=filters, filters=filters, fields=["*"]
    )
    for row in st_list:
        dd_date = row.dd_date or add_days(today(), -1)
        # if get_next_calendar_date(row.calendar, dd_date, validate=True) == False:
        #     st_doc = frappe.get_doc("SchTask Control Table", row.name)
        #     st_doc.add_comment(
        #         "Comment",
        #         "{0}:No future date exists for mention calendar".format(today()),
        #     )
        #     frappe.log_error(
        #         title="ST Management Cron Error {0}".format(row.name),
        #         message="{0}:No future date exists for mention calendar".format(
        #             today()
        #         ),
        #     )
        #     continue
        try:
            model_doc = create_blank_entry(row)
            if not model_doc == False:
                todo_doc = create_todo(row, model_doc)
                if not todo_doc == False:
                    update_stct(row, todo_doc)
        except Exception as e:
            frappe.log_error(
                title="SchTask Control Error", message=frappe.get_traceback()
            )


@frappe.whitelist()
def send_first_reminder():
    filters = [
        ["first_rem_date", "<=", today()],
        ["first_rem_sent_on", "is", "not set"],
        ["stop_reminders", "=", 0],
        ["status", "!=", "Completed"],
    ]
    todos = frappe.get_all(
        "Todo Items",
        filters=filters,
        fields=["*"],
        order_by="dd_date asc,series asc,name asc",
    )
    todo_data = {}
    for todo in todos:
        stop_reminder = frappe.db.get_value(
            "SchTask Control Table", todo.get("schtask_control_table"), "stop_reminders"
        )
        # stop_escalation = frappe.db.get_value(
        #     "SchTask Control Table",
        #     todo.get("schtask_control_table"),
        #     "stop_escalation",
        # )
        todo["dd_date"] = format_date(todo.get("dd_date"))
        if not stop_reminder:
            email_id = frappe.db.get_value("Position", todo.get("position"), "email_id")
            if email_id:
                if not todo_data.get(email_id):
                    todo_data[email_id] = [todo]
                else:
                    todo_data[email_id].append(todo)
    print(todo_data)

    send_email_reminder("First Reminder Template", todo_data, reminder_type="first")


@frappe.whitelist()
def send_final_reminder():
    filters = [
        ["final_rem_date", "<=", today()],
        ["final_rem_sent_on", "is", "not set"],
        ["stop_reminders", "=", 0],
        ["status", "!=", "Completed"],
    ]
    todos = frappe.get_all(
        "Todo Items",
        filters=filters,
        fields=["*"],
        order_by="dd_date asc,series asc,name asc",
    )
    todo_data = {}
    for todo in todos:
        stop_reminder = frappe.db.get_value(
            "SchTask Control Table", todo.get("schtask_control_table"), "stop_reminders"
        )
        # stop_escalation = frappe.db.get_value(
        #     "SchTask Control Table",
        #     todo.get("schtask_control_table"),
        #     "stop_escalation",
        # )
        todo["dd_date"] = format_date(todo.get("dd_date"))
        if not stop_reminder:
            email_id = frappe.db.get_value("Position", todo.get("position"), "email_id")
            if email_id:
                if not todo_data.get(email_id):
                    todo_data[email_id] = [todo]
                else:
                    todo_data[email_id].append(todo)
    print(todo_data)
    send_email_reminder("Final Reminder", todo_data, reminder_type="final")


@frappe.whitelist()
def send_escalation_reminder():
    filters = [
        ["escalation_date", "<=", today()],
        ["stop_escalation", "=", 0],
        ["status", "!=", "Completed"],
    ]
    todos = frappe.get_all(
        "Todo Items",
        filters=filters,
        fields=["*"],
        order_by="dd_date asc,series asc,name asc",
    )
    todo_data = {}
    todo_data_manager = {}

    for todo in todos:
        stop_escalation = frappe.db.get_value(
            "SchTask Control Table",
            todo.get("schtask_control_table"),
            "stop_escalation",
        )
        todo["dd_date"] = format_date(todo.get("dd_date"))
        if not stop_escalation:
            # email_id = frappe.db.get_value("Position", todo.get("position"), "email_id")
            # if email_id:
            #     if not todo_data.get(email_id):
            #         todo_data[email_id] = [todo]
            #     else:
            #         todo_data[email_id].append(todo)
            email_id_manager = frappe.db.get_value(
                "Position", todo.get("escalation_position"), "email_id"
            )
            if email_id_manager:
                if not todo_data_manager.get(email_id_manager):
                    todo_data_manager[email_id_manager] = [todo]
                else:
                    todo_data_manager[email_id_manager].append(todo)
    # send_email_reminder("Escalation Reminder", todo_data, reminder_type="escalation")
    send_email_reminder(
        "Escalation Reminder", todo_data_manager, reminder_type="escalation"
    )


def send_email_reminder(template, data, reminder_type=None):
    try:
        template_doc = frappe.get_doc("Email Template", template)
        for key, value in data.items():
            if value:
                position = (
                    frappe.db.get_value("Position", {"email_id": key}, "name") or ""
                )
                context = {"todos": value, "position": position}
                frappe.sendmail(
                    recipients=key,
                    subject=template_doc.subject,
                    message=frappe.render_template(template_doc.response_html, context),
                )
                if reminder_type:
                    update_todo_items(value, reminder_type=reminder_type)
    except Exception as e:
        frappe.log_error(
            title="Error During Sending Reminder", message=frappe.get_traceback()
        )


def update_todo_items(todos, reminder_type):
    field_map = {
        "first": "first_rem_sent_on",
        "final": "final_rem_sent_on",
        "escalation": "last_escalated_on",
    }
    field = field_map.get(reminder_type)
    if field:
        for todo in todos:
            frappe.db.set_value("Todo Items", todo.get("name"), field, now_datetime())
            if reminder_type == "escalation":
                reminder_profile = frappe.db.get_value(
                    "SchTask Control Table",
                    todo.schtask_control_table,
                    "reminder_profile",
                )
                calendar = frappe.db.get_value(
                    "Reminder Profile", reminder_profile, "escalation_calendar"
                )
                next_escalation_date = get_next_calendar_date(
                    calendar, todo.escalation_date, reminder=True
                )
                if next_escalation_date:
                    frappe.db.set_value(
                        "Todo Items", todo.get("name"), field, now_datetime()
                    )
                    frappe.db.set_value(
                        "Todo Items",
                        todo.get("name"),
                        "escalation_date",
                        next_escalation_date,
                    )
            else:
                frappe.db.set_value(
                    "Todo Items", todo.get("name"), field, now_datetime()
                )


def update_status_in_todo(self, method):
    stct = frappe.db.sql(
        """select distinct model from `tabSchTask Control Table`""", as_dict=1
    )
    doctypes = [row.model for row in stct]
    if self.doctype in doctypes:
        if self.get("status"):
            frappe.db.set_value(
                "Todo Items",
                {"model": self.doctype, "model_name": self.name},
                "status",
                self.status,
            )
