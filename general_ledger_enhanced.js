// Copyright (c) 2024, ERPNext Pro System and contributors
// License: MIT

frappe.query_reports["General Ledger Enhanced"] = {
    "filters": [
        // Company (Required)
        {
            "fieldname": "company",
            "label": __("Company"),
            "fieldtype": "Link",
            "options": "Company",
            "default": frappe.defaults.get_user_default("Company"),
            "reqd": 1,
            "width": "100px"
        },
        
        // Finance Book
        {
            "fieldname": "finance_book",
            "label": __("Finance Book"),
            "fieldtype": "Link",
            "options": "Finance Book",
            "width": "100px"
        },
        
        // From Date (Required)
        {
            "fieldname": "from_date",
            "label": __("From Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.add_months(frappe.datetime.get_today(), -1),
            "reqd": 1,
            "width": "100px"
        },
        
        // To Date (Required)
        {
            "fieldname": "to_date",
            "label": __("To Date"),
            "fieldtype": "Date",
            "default": frappe.datetime.get_today(),
            "reqd": 1,
            "width": "100px"
        },
        
        // Account (Multi-select)
        {
            "fieldname": "account",
            "label": __("Account"),
            "fieldtype": "MultiSelectList",
            "options": "Account",
            "get_data": function(txt) {
                return frappe.db.get_link_options('Account', txt, {
                    company: frappe.query_report.get_filter_value("company")
                });
            },
            "width": "150px"
        },
        
        // Voucher No
        {
            "fieldname": "voucher_no",
            "label": __("Voucher No"),
            "fieldtype": "Data",
            "width": "120px"
        },
        
        // Against Voucher No
        {
            "fieldname": "against_voucher_no",
            "label": __("Against Voucher No"),
            "fieldtype": "Data",
            "width": "120px"
        },
        
        // Party Type
        {
            "fieldname": "party_type",
            "label": __("Party Type"),
            "fieldtype": "Link",
            "options": "DocType",
            "get_query": function() {
                return {
                    filters: {
                        "name": ["in", ["Customer", "Supplier", "Employee", "Shareholder", "Member"]]
                    }
                }
            },
            "width": "100px",
            "on_change": function() {
                frappe.query_report.set_filter_value('party', "");
            }
        },
        
        // Party (Dynamic based on Party Type)
        {
            "fieldname": "party",
            "label": __("Party"),
            "fieldtype": "MultiSelectList",
            "get_data": function(txt) {
                if (!frappe.query_report.get_filter_value('party_type')) {
                    frappe.throw(__("Please select Party Type first"));
                }
                return frappe.db.get_link_options(frappe.query_report.get_filter_value('party_type'), txt);
            },
            "width": "150px"
        },
        
        // Project (Multi-select)
        {
            "fieldname": "project",
            "label": __("Project"),
            "fieldtype": "MultiSelectList",
            "options": "Project",
            "get_data": function(txt) {
                return frappe.db.get_link_options('Project', txt, {
                    company: frappe.query_report.get_filter_value("company")
                });
            },
            "width": "120px"
        },
        
        // Cost Center (Multi-select with children)
        {
            "fieldname": "cost_center",
            "label": __("Cost Center"),
            "fieldtype": "MultiSelectList",
            "options": "Cost Center",
            "get_data": function(txt) {
                return frappe.db.get_link_options('Cost Center', txt, {
                    company: frappe.query_report.get_filter_value("company")
                });
            },
            "width": "120px"
        },
        
        // Against Account
        {
            "fieldname": "against",
            "label": __("Against Account"),
            "fieldtype": "Data",
            "width": "120px"
        },
        
        // Group By
        {
            "fieldname": "group_by",
            "label": __("Group By"),
            "fieldtype": "Select",
            "options": [
                "",
                { "value": "Group by Voucher", "label": __("Group by Voucher") },
                { "value": "Group by Voucher (Consolidated)", "label": __("Group by Voucher (Consolidated)") },
                { "value": "Group by Account", "label": __("Group by Account") },
                { "value": "Group by Party", "label": __("Group by Party") }
            ],
            "default": "Group by Voucher (Consolidated)",
            "width": "120px"
        },
        
        // Tax ID
        {
            "fieldname": "tax_id",
            "label": __("Tax ID"),
            "fieldtype": "Data",
            "width": "100px"
        },
        
        // Presentation Currency
        {
            "fieldname": "presentation_currency",
            "label": __("Currency"),
            "fieldtype": "Link",
            "options": "Currency",
            "default": frappe.defaults.get_user_default("Currency"),
            "width": "100px"
        },
        
        // --- Checkbox Filters ---
        
        // Show Cancelled Entries
        {
            "fieldname": "show_cancelled_entries",
            "label": __("Show Cancelled Entries"),
            "fieldtype": "Check",
            "default": 0
        },
        
        // Show Opening Entries
        {
            "fieldname": "show_opening_entries",
            "label": __("Show Opening Entries"),
            "fieldtype": "Check",
            "default": 1
        },
        
        // Include Dimensions
        {
            "fieldname": "include_dimensions",
            "label": __("Include Dimensions"),
            "fieldtype": "Check",
            "default": 0
        },
        
        // Show Remarks
        {
            "fieldname": "show_remarks",
            "label": __("Show Remarks"),
            "fieldtype": "Check",
            "default": 0
        },
        
        // Show Party Name
        {
            "fieldname": "show_party_name",
            "label": __("Show Party Name"),
            "fieldtype": "Check",
            "default": 0
        },
        
        // Include Default Book Entries
        {
            "fieldname": "include_default_book_entries",
            "label": __("Include Default FB Entries"),
            "fieldtype": "Check",
            "default": 1
        },
        
        // Show Net Values in Party Account
        {
            "fieldname": "show_net_values_in_party_account",
            "label": __("Show Net Values in Party Account"),
            "fieldtype": "Check",
            "default": 0
        },
        
        // Add Values in Transaction Currency
        {
            "fieldname": "add_values_in_transaction_currency",
            "label": __("Show Values in Transaction Currency"),
            "fieldtype": "Check",
            "default": 0
        },
        
        // Show Debit/Credit Separately
        {
            "fieldname": "show_debit_credit_separately",
            "label": __("Show Debit/Credit Separately"),
            "fieldtype": "Check",
            "default": 0
        }
    ],
    
    "formatter": function(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);
        
        // Highlight opening balance row
        if (data && data.is_opening) {
            value = "<span style='color: #667eea; font-weight: bold;'>" + value + "</span>";
        }
        
        // Highlight cancelled entries
        if (data && data.is_cancelled) {
            value = "<span style='color: #eb3349; text-decoration: line-through;'>" + value + "</span>";
        }
        
        // Format balance column with color coding
        if (column.fieldname === "balance") {
            if (data && data.balance !== undefined) {
                const balance = parseFloat(data.balance);
                if (balance > 0) {
                    value = "<span style='color: #11998e; font-weight: 600;'>" + value + "</span>";
                } else if (balance < 0) {
                    value = "<span style='color: #eb3349; font-weight: 600;'>" + value + "</span>";
                }
            }
        }
        
        // Make voucher numbers clickable
        if (column.fieldname === "voucher_no" && data && data.voucher_type) {
            value = `<a href="/app/${frappe.router.slug(data.voucher_type)}/${data.voucher_no}" 
                        style="color: #667eea; text-decoration: underline;">${value}</a>`;
        }
        
        return value;
    },
    
    "onload": function(report) {
        // Add custom buttons
        report.page.add_inner_button(__("Export to Excel"), function() {
            frappe.query_report.export_report('xlsx');
        });
        
        report.page.add_inner_button(__("Print"), function() {
            frappe.query_report.print_report();
        });
        
        // Add refresh button
        report.page.set_secondary_action(__("Refresh"), function() {
            frappe.query_report.refresh();
        });
    },
    
    "after_datatable_render": function(datatable_obj) {
        // Add custom styling after table renders
        $(datatable_obj.wrapper).find('.dt-scrollable').css({
            'max-height': '70vh',
            'overflow-y': 'auto'
        });
    },
    
    "get_datatable_options": function(options) {
        return Object.assign(options, {
            checkboxColumn: false,
            events: {
                onRemoveColumn: function(column) {
                    console.log('Column removed:', column);
                },
                onSwitchColumn: function(column1, column2) {
                    console.log('Columns switched:', column1, column2);
                },
                onSortColumn: function(column) {
                    console.log('Column sorted:', column);
                }
            }
        });
    }
};

// Helper function to format currency
function formatCurrency(value, currency) {
    if (!value) return "0.00";
    return parseFloat(value).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    }) + " " + (currency || "SAR");
}

// Helper function to get fiscal year dates
function getFiscalYearDates() {
    frappe.call({
        method: "erpnext.accounts.utils.get_fiscal_year",
        args: {
            date: frappe.datetime.get_today(),
            company: frappe.query_report.get_filter_value("company")
        },
        callback: function(r) {
            if (r.message) {
                frappe.query_report.set_filter_value('from_date', r.message[1]);
                frappe.query_report.set_filter_value('to_date', r.message[2]);
            }
        }
    });
}
