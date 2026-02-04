# Copyright (c) 2024, ERPNext Pro System and contributors
# License: MIT

import frappe
from frappe import _
from frappe.utils import flt, getdate, cstr, fmt_money
from erpnext.accounts.report.financial_statements import get_cost_centers_with_children
from erpnext.accounts.doctype.accounting_dimension.accounting_dimension import (
    get_accounting_dimensions,
    get_dimension_with_children,
)
from pypika.terms import Case

def execute(filters=None):
    """Main execution function for General Ledger Report"""
    
    if not filters:
        filters = {}
    
    validate_filters(filters)
    
    # Get data
    data = get_gl_entries(filters)
    
    # Get columns
    columns = get_columns(filters)
    
    # Calculate summary
    message = get_report_summary(data, filters)
    
    # Add charts
    chart = get_chart_data(data, filters)
    
    return columns, data, message, chart


def validate_filters(filters):
    """Validate filter inputs"""
    
    if not filters.get("company"):
        frappe.throw(_("Company is mandatory"))
    
    if not filters.get("from_date") or not filters.get("to_date"):
        frappe.throw(_("From Date and To Date are mandatory"))
    
    if getdate(filters.from_date) > getdate(filters.to_date):
        frappe.throw(_("From Date cannot be greater than To Date"))
    
    # Set default presentation currency
    if not filters.get("presentation_currency"):
        filters["presentation_currency"] = frappe.get_cached_value(
            "Company", filters.company, "default_currency"
        )


def get_columns(filters):
    """Define report columns"""
    
    columns = [
        {
            "label": _("Posting Date"),
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 90
        },
        {
            "label": _("Account"),
            "fieldname": "account",
            "fieldtype": "Link",
            "options": "Account",
            "width": 200
        }
    ]
    
    # Add debit/credit columns
    if filters.get("show_debit_credit_separately"):
        columns.extend([
            {
                "label": _("Debit"),
                "fieldname": "debit",
                "fieldtype": "Currency",
                "width": 120
            },
            {
                "label": _("Credit"),
                "fieldname": "credit",
                "fieldtype": "Currency",
                "width": 120
            }
        ])
    else:
        columns.append({
            "label": _("Debit"),
            "fieldname": "debit",
            "fieldtype": "Currency",
            "width": 120
        })
        columns.append({
            "label": _("Credit"),
            "fieldname": "credit",
            "fieldtype": "Currency",
            "width": 120
        })
    
    # Balance column
    columns.append({
        "label": _("Balance"),
        "fieldname": "balance",
        "fieldtype": "Currency",
        "width": 130
    })
    
    # Voucher details
    columns.extend([
        {
            "label": _("Voucher Type"),
            "fieldname": "voucher_type",
            "width": 120
        },
        {
            "label": _("Voucher No"),
            "fieldname": "voucher_no",
            "fieldtype": "Dynamic Link",
            "options": "voucher_type",
            "width": 180
        },
        {
            "label": _("Against Account"),
            "fieldname": "against",
            "width": 200
        }
    ])
    
    # Party columns
    if filters.get("party_type") or filters.get("party"):
        columns.extend([
            {
                "label": _("Party Type"),
                "fieldname": "party_type",
                "width": 100
            },
            {
                "label": _("Party"),
                "fieldname": "party",
                "fieldtype": "Dynamic Link",
                "options": "party_type",
                "width": 150
            }
        ])
        
        if filters.get("show_party_name"):
            columns.append({
                "label": _("Party Name"),
                "fieldname": "party_name",
                "fieldtype": "Data",
                "width": 150
            })
    
    # Cost Center & Project
    columns.extend([
        {
            "label": _("Cost Center"),
            "fieldname": "cost_center",
            "fieldtype": "Link",
            "options": "Cost Center",
            "width": 120
        },
        {
            "label": _("Project"),
            "fieldname": "project",
            "fieldtype": "Link",
            "options": "Project",
            "width": 120
        }
    ])
    
    # Finance Book
    if filters.get("finance_book"):
        columns.append({
            "label": _("Finance Book"),
            "fieldname": "finance_book",
            "fieldtype": "Link",
            "options": "Finance Book",
            "width": 100
        })
    
    # Accounting Dimensions
    if filters.get("include_dimensions"):
        for dimension in get_accounting_dimensions(as_list=False):
            columns.append({
                "label": _(dimension.label),
                "fieldname": dimension.fieldname,
                "fieldtype": "Link",
                "options": dimension.label,
                "width": 100
            })
    
    # Transaction Currency Columns
    if filters.get("add_values_in_transaction_currency"):
        columns.extend([
            {
                "label": _("Debit (Transaction Currency)"),
                "fieldname": "debit_in_transaction_currency",
                "fieldtype": "Currency",
                "options": "account_currency",
                "width": 150
            },
            {
                "label": _("Credit (Transaction Currency)"),
                "fieldname": "credit_in_transaction_currency",
                "fieldtype": "Currency",
                "options": "account_currency",
                "width": 150
            },
            {
                "label": _("Transaction Currency"),
                "fieldname": "account_currency",
                "fieldtype": "Link",
                "options": "Currency",
                "width": 100
            }
        ])
    
    # Remarks
    if filters.get("show_remarks"):
        columns.append({
            "label": _("Remarks"),
            "fieldname": "remarks",
            "fieldtype": "Data",
            "width": 200
        })
    
    # Against Voucher
    columns.extend([
        {
            "label": _("Against Voucher Type"),
            "fieldname": "against_voucher_type",
            "width": 100
        },
        {
            "label": _("Against Voucher"),
            "fieldname": "against_voucher",
            "fieldtype": "Dynamic Link",
            "options": "against_voucher_type",
            "width": 150
        }
    ])
    
    return columns


def get_gl_entries(filters):
    """Fetch GL entries based on filters"""
    
    # Build query conditions
    conditions = get_conditions(filters)
    
    # Build query
    gl_entries = frappe.db.sql(
        """
        SELECT
            gle.name,
            gle.posting_date,
            gle.account,
            gle.party_type,
            gle.party,
            gle.cost_center,
            gle.project,
            gle.against,
            gle.account_currency,
            gle.debit,
            gle.credit,
            gle.debit_in_account_currency,
            gle.credit_in_account_currency,
            gle.against_voucher_type,
            gle.against_voucher,
            gle.voucher_type,
            gle.voucher_no,
            gle.voucher_detail_no,
            gle.remarks,
            gle.is_opening,
            gle.is_cancelled,
            gle.finance_book,
            gle.to_rename,
            gle.due_date,
            acc.account_name,
            acc.account_number,
            party.customer_name,
            party.supplier_name
        FROM 
            `tabGL Entry` gle
        LEFT JOIN 
            `tabAccount` acc ON gle.account = acc.name
        LEFT JOIN 
            `tabCustomer` party ON gle.party = party.name AND gle.party_type = 'Customer'
        LEFT JOIN 
            `tabSupplier` party2 ON gle.party = party2.name AND gle.party_type = 'Supplier'
        WHERE 
            gle.company = %(company)s
            AND gle.posting_date BETWEEN %(from_date)s AND %(to_date)s
            {conditions}
        ORDER BY 
            gle.posting_date, gle.account, gle.creation
        """.format(conditions=conditions),
        filters,
        as_dict=1
    )
    
    # Process entries
    data = []
    opening_balance = 0
    running_balance = 0
    
    # Get opening balance if needed
    if filters.get("show_opening_entries"):
        opening_balance = get_opening_balance(filters)
        if opening_balance != 0:
            data.append({
                "posting_date": filters.from_date,
                "account": _("Opening Balance"),
                "debit": opening_balance if opening_balance > 0 else 0,
                "credit": abs(opening_balance) if opening_balance < 0 else 0,
                "balance": opening_balance,
                "is_opening": 1
            })
            running_balance = opening_balance
    
    # Process GL entries
    for entry in gl_entries:
        # Calculate balance
        running_balance += flt(entry.debit) - flt(entry.credit)
        
        # Add to data
        row = {
            "posting_date": entry.posting_date,
            "account": entry.account,
            "account_name": entry.account_name,
            "debit": flt(entry.debit),
            "credit": flt(entry.credit),
            "balance": running_balance,
            "voucher_type": entry.voucher_type,
            "voucher_no": entry.voucher_no,
            "against": entry.against,
            "party_type": entry.party_type,
            "party": entry.party,
            "cost_center": entry.cost_center,
            "project": entry.project,
            "remarks": entry.remarks if filters.get("show_remarks") else "",
            "against_voucher_type": entry.against_voucher_type,
            "against_voucher": entry.against_voucher,
            "is_opening": entry.is_opening,
            "is_cancelled": entry.is_cancelled
        }
        
        # Add party name if requested
        if filters.get("show_party_name"):
            if entry.party_type == "Customer":
                row["party_name"] = entry.customer_name
            elif entry.party_type == "Supplier":
                row["party_name"] = entry.supplier_name
        
        # Add transaction currency values
        if filters.get("add_values_in_transaction_currency"):
            row["debit_in_transaction_currency"] = entry.debit_in_account_currency
            row["credit_in_transaction_currency"] = entry.credit_in_account_currency
            row["account_currency"] = entry.account_currency
        
        # Add finance book
        if filters.get("finance_book"):
            row["finance_book"] = entry.finance_book
        
        data.append(row)
    
    return data


def get_conditions(filters):
    """Build SQL conditions based on filters"""
    
    conditions = []
    
    # Account filter
    if filters.get("account"):
        accounts = filters.account
        if isinstance(accounts, str):
            accounts = [accounts]
        conditions.append(f"gle.account IN {tuple(accounts)}")
    
    # Voucher No filter
    if filters.get("voucher_no"):
        conditions.append(f"gle.voucher_no = '{filters.voucher_no}'")
    
    # Against Voucher filter
    if filters.get("against_voucher_no"):
        conditions.append(f"gle.against_voucher = '{filters.against_voucher_no}'")
    
    # Party Type filter
    if filters.get("party_type"):
        conditions.append(f"gle.party_type = '{filters.party_type}'")
    
    # Party filter
    if filters.get("party"):
        parties = filters.party
        if isinstance(parties, str):
            parties = [parties]
        conditions.append(f"gle.party IN {tuple(parties)}")
    
    # Cost Center filter
    if filters.get("cost_center"):
        cost_centers = get_cost_centers_with_children(filters.cost_center)
        conditions.append(f"gle.cost_center IN {tuple(cost_centers)}")
    
    # Project filter
    if filters.get("project"):
        projects = filters.project
        if isinstance(projects, str):
            projects = [projects]
        conditions.append(f"gle.project IN {tuple(projects)}")
    
    # Finance Book filter
    if filters.get("finance_book"):
        conditions.append(f"(gle.finance_book = '{filters.finance_book}' OR gle.finance_book IS NULL)")
    
    # Show cancelled entries
    if not filters.get("show_cancelled_entries"):
        conditions.append("gle.is_cancelled = 0")
    
    # Tax ID filter
    if filters.get("tax_id"):
        conditions.append(f"gle.tax_id = '{filters.tax_id}'")
    
    # Against filter
    if filters.get("against"):
        conditions.append(f"gle.against LIKE '%{filters.against}%'")
    
    return " AND " + " AND ".join(conditions) if conditions else ""


def get_opening_balance(filters):
    """Calculate opening balance"""
    
    conditions = get_conditions(filters)
    
    opening = frappe.db.sql(
        """
        SELECT 
            SUM(debit) - SUM(credit) as opening_balance
        FROM 
            `tabGL Entry`
        WHERE 
            company = %(company)s
            AND posting_date < %(from_date)s
            {conditions}
        """.format(conditions=conditions),
        filters,
        as_dict=1
    )
    
    return flt(opening[0].opening_balance) if opening else 0


def get_report_summary(data, filters):
    """Generate report summary"""
    
    if not data:
        return []
    
    total_debit = sum(flt(d.get("debit", 0)) for d in data if not d.get("is_opening"))
    total_credit = sum(flt(d.get("credit", 0)) for d in data if not d.get("is_opening"))
    closing_balance = total_debit - total_credit
    
    currency = filters.get("presentation_currency")
    
    return [
        {
            "value": fmt_money(total_debit, currency=currency),
            "label": _("Total Debit"),
            "datatype": "Currency",
            "indicator": "Blue"
        },
        {
            "value": fmt_money(total_credit, currency=currency),
            "label": _("Total Credit"),
            "datatype": "Currency",
            "indicator": "Blue"
        },
        {
            "value": fmt_money(closing_balance, currency=currency),
            "label": _("Closing Balance"),
            "datatype": "Currency",
            "indicator": "Green" if closing_balance >= 0 else "Red"
        }
    ]


def get_chart_data(data, filters):
    """Generate chart data for visualization"""
    
    if not data or len(data) < 2:
        return None
    
    # Group by month
    monthly_data = {}
    
    for row in data:
        if row.get("is_opening"):
            continue
            
        month = getdate(row.get("posting_date")).strftime("%Y-%m")
        
        if month not in monthly_data:
            monthly_data[month] = {"debit": 0, "credit": 0}
        
        monthly_data[month]["debit"] += flt(row.get("debit", 0))
        monthly_data[month]["credit"] += flt(row.get("credit", 0))
    
    # Sort by month
    sorted_months = sorted(monthly_data.keys())
    
    labels = [getdate(m + "-01").strftime("%b %Y") for m in sorted_months]
    debit_values = [monthly_data[m]["debit"] for m in sorted_months]
    credit_values = [monthly_data[m]["credit"] for m in sorted_months]
    
    return {
        "data": {
            "labels": labels,
            "datasets": [
                {
                    "name": _("Debit"),
                    "values": debit_values
                },
                {
                    "name": _("Credit"),
                    "values": credit_values
                }
            ]
        },
        "type": "bar",
        "colors": ["#667eea", "#764ba2"],
        "barOptions": {
            "stacked": 0
        }
    }
