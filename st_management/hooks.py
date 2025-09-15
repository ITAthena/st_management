from . import __version__ as app_version

app_name = "st_management"
app_title = "St Management"
app_publisher = "Bhavesh Maheshwari"
app_description = "Schedule Task Management"
app_email = "info@nesscale.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/st_management/css/st_management.css"
# app_include_js = "/assets/st_management/js/st_management.js"

# include js, css files in header of web template
# web_include_css = "/assets/st_management/css/st_management.css"
# web_include_js = "/assets/st_management/js/st_management.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "st_management/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "st_management.utils.jinja_methods",
# 	"filters": "st_management.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "st_management.install.before_install"
# after_install = "st_management.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "st_management.uninstall.before_uninstall"
# after_uninstall = "st_management.uninstall.after_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "st_management.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {"*": {"validate": "st_management.utils.helper.update_status_in_todo"}}

# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "st_management.utils.helper.cron_st",
        "st_management.utils.helper.send_first_reminder",
        "st_management.utils.helper.send_final_reminder",
        "st_management.utils.helper.send_escalation_reminder",
    ],
    "cron": {
        "00 06 * * *": [
            "leo.loe.doctype.leo_appointment.leo_appointment.appointment_reminder"
        ]
    },
}

fixtures = [
    {
        "dt": "Email Template",
    }
]

# Testing
# -------

# before_tests = "st_management.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "st_management.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "st_management.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]


# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"st_management.auth.validate"
# ]

# Translation
# --------------------------------

# Make link fields search translated document names for these DocTypes
# Recommended only for DocTypes which have limited documents with untranslated names
# For example: Role, Gender, etc.
# translated_search_doctypes = []
