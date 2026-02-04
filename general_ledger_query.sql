-- =================================================================
-- GENERAL LEDGER ENHANCED - SQL QUERY
-- ERPNext Pro System - Complete Query with All Filters
-- =================================================================

-- This query includes all standard GL Entry fields and supports
-- all the filters defined in the enhanced report

SELECT
    -- Basic GL Entry Fields
    `tabGL Entry`.name AS 'name:Link/GL Entry:100',
    `tabGL Entry`.posting_date AS 'تاريخ الترحيل:Date:100',
    `tabGL Entry`.creation AS 'creation:Datetime:150',
    
    -- Account Information
    `tabGL Entry`.account AS 'الحساب:Link/Account:200',
    `tabAccount`.account_name AS 'اسم الحساب:Data:180',
    `tabAccount`.account_number AS 'رقم الحساب:Data:100',
    `tabAccount`.account_type AS 'نوع الحساب:Data:120',
    `tabAccount`.root_type AS 'النوع الجذري:Data:100',
    
    -- Debit and Credit
    `tabGL Entry`.debit AS 'مدين:Currency:120',
    `tabGL Entry`.credit AS 'دائن:Currency:120',
    
    -- Running Balance (Calculated)
    (
        SELECT 
            SUM(gle_inner.debit - gle_inner.credit)
        FROM 
            `tabGL Entry` gle_inner
        WHERE 
            gle_inner.company = `tabGL Entry`.company
            AND gle_inner.posting_date <= `tabGL Entry`.posting_date
            AND (
                gle_inner.posting_date < `tabGL Entry`.posting_date
                OR gle_inner.creation <= `tabGL Entry`.creation
            )
            -- Apply same account filter if specified
            AND (
                %(account)s IS NULL 
                OR gle_inner.account = `tabGL Entry`.account
            )
    ) AS 'الرصيد:Currency:130',
    
    -- Voucher Information
    `tabGL Entry`.voucher_type AS 'نوع القيد:Data:120',
    `tabGL Entry`.voucher_no AS 'رقم القيد:Dynamic Link/voucher_type:180',
    `tabGL Entry`.voucher_detail_no AS 'رقم تفاصيل القيد:Data:150',
    
    -- Against Account
    `tabGL Entry`.against AS 'ضد الحساب:Data:200',
    `tabGL Entry`.against_voucher_type AS 'نوع القيد المقابل:Data:120',
    `tabGL Entry`.against_voucher AS 'القيد المقابل:Dynamic Link/against_voucher_type:150',
    
    -- Party Information
    `tabGL Entry`.party_type AS 'نوع الطرف:Data:100',
    `tabGL Entry`.party AS 'الطرف:Dynamic Link/party_type:150',
    
    -- Party Names (Customer or Supplier)
    COALESCE(
        `tabCustomer`.customer_name,
        `tabSupplier`.supplier_name,
        `tabEmployee`.employee_name,
        ''
    ) AS 'اسم الطرف:Data:180',
    
    -- Cost Center and Project
    `tabGL Entry`.cost_center AS 'مركز التكلفة:Link/Cost Center:120',
    `tabCost Center`.cost_center_name AS 'اسم مركز التكلفة:Data:150',
    `tabGL Entry`.project AS 'المشروع:Link/Project:120',
    `tabProject`.project_name AS 'اسم المشروع:Data:150',
    
    -- Finance Book
    `tabGL Entry`.finance_book AS 'دفتر المالي:Link/Finance Book:100',
    
    -- Currency Information
    `tabGL Entry`.account_currency AS 'عملة الحساب:Link/Currency:100',
    `tabGL Entry`.debit_in_account_currency AS 'مدين (عملة الحساب):Currency:150',
    `tabGL Entry`.credit_in_account_currency AS 'دائن (عملة الحساب):Currency:150',
    
    -- Remarks and User
    `tabGL Entry`.remarks AS 'ملاحظات:Data:300',
    `tabGL Entry`.user_remarks AS 'ملاحظات المستخدم:Data:300',
    
    -- Status and Flags
    `tabGL Entry`.is_opening AS 'قيد افتتاحي:Check:80',
    `tabGL Entry`.is_cancelled AS 'ملغى:Check:80',
    `tabGL Entry`.is_advance AS 'سلفة:Check:80',
    `tabGL Entry`.fiscal_year AS 'السنة المالية:Link/Fiscal Year:100',
    
    -- Due Date (for receivables/payables)
    `tabGL Entry`.due_date AS 'تاريخ الاستحقاق:Date:100',
    
    -- Tax Information
    `tabGL Entry`.tax_id AS 'الرقم الضريبي:Data:120',
    
    -- Additional Fields
    `tabGL Entry`.company AS 'الشركة:Link/Company:150',
    `tabGL Entry`.to_rename AS 'to_rename:Int:50',
    `tabGL Entry`.docstatus AS 'حالة المستند:Int:50',
    
    -- Created and Modified Info
    `tabGL Entry`.owner AS 'المنشئ:Link/User:150',
    `tabGL Entry`.modified AS 'modified:Datetime:150',
    `tabGL Entry`.modified_by AS 'modified_by:Link/User:150'

FROM 
    `tabGL Entry`

-- JOIN Account Table
LEFT JOIN 
    `tabAccount` 
    ON `tabGL Entry`.account = `tabAccount`.name

-- JOIN Cost Center Table
LEFT JOIN 
    `tabCost Center` 
    ON `tabGL Entry`.cost_center = `tabCost Center`.name

-- JOIN Project Table
LEFT JOIN 
    `tabProject` 
    ON `tabGL Entry`.project = `tabProject`.name

-- JOIN Customer Table (for party_type = 'Customer')
LEFT JOIN 
    `tabCustomer` 
    ON `tabGL Entry`.party = `tabCustomer`.name 
    AND `tabGL Entry`.party_type = 'Customer'

-- JOIN Supplier Table (for party_type = 'Supplier')
LEFT JOIN 
    `tabSupplier` 
    ON `tabGL Entry`.party = `tabSupplier`.name 
    AND `tabGL Entry`.party_type = 'Supplier'

-- JOIN Employee Table (for party_type = 'Employee')
LEFT JOIN 
    `tabEmployee` 
    ON `tabGL Entry`.party = `tabEmployee`.name 
    AND `tabGL Entry`.party_type = 'Employee'

WHERE 
    -- Company Filter (Required)
    `tabGL Entry`.company = %(company)s
    
    -- Date Range Filter (Required)
    AND `tabGL Entry`.posting_date BETWEEN %(from_date)s AND %(to_date)s
    
    -- Account Filter (Multi-select support)
    AND (
        %(account)s IS NULL 
        OR `tabGL Entry`.account IN %(account)s
    )
    
    -- Voucher No Filter
    AND (
        %(voucher_no)s IS NULL 
        OR %(voucher_no)s = ''
        OR `tabGL Entry`.voucher_no = %(voucher_no)s
    )
    
    -- Against Voucher Filter
    AND (
        %(against_voucher_no)s IS NULL 
        OR %(against_voucher_no)s = ''
        OR `tabGL Entry`.against_voucher = %(against_voucher_no)s
    )
    
    -- Party Type Filter
    AND (
        %(party_type)s IS NULL 
        OR %(party_type)s = ''
        OR `tabGL Entry`.party_type = %(party_type)s
    )
    
    -- Party Filter (Multi-select support)
    AND (
        %(party)s IS NULL 
        OR `tabGL Entry`.party IN %(party)s
    )
    
    -- Project Filter (Multi-select support)
    AND (
        %(project)s IS NULL 
        OR `tabGL Entry`.project IN %(project)s
    )
    
    -- Cost Center Filter (Multi-select support)
    AND (
        %(cost_center)s IS NULL 
        OR `tabGL Entry`.cost_center IN %(cost_center)s
    )
    
    -- Against Account Filter
    AND (
        %(against)s IS NULL 
        OR %(against)s = ''
        OR `tabGL Entry`.against LIKE CONCAT('%', %(against)s, '%')
    )
    
    -- Finance Book Filter
    AND (
        %(finance_book)s IS NULL 
        OR %(finance_book)s = ''
        OR `tabGL Entry`.finance_book = %(finance_book)s
        OR (
            %(include_default_book_entries)s = 1 
            AND `tabGL Entry`.finance_book IS NULL
        )
    )
    
    -- Tax ID Filter
    AND (
        %(tax_id)s IS NULL 
        OR %(tax_id)s = ''
        OR `tabGL Entry`.tax_id = %(tax_id)s
    )
    
    -- Show Cancelled Entries Filter
    AND (
        %(show_cancelled_entries)s = 1 
        OR `tabGL Entry`.is_cancelled = 0
    )
    
    -- Show Opening Entries Filter
    AND (
        %(show_opening_entries)s = 1 
        OR `tabGL Entry`.is_opening = 0
    )
    
    -- Document Status (only submitted entries)
    AND `tabGL Entry`.docstatus = 1

ORDER BY 
    `tabGL Entry`.posting_date ASC,
    `tabGL Entry`.account ASC,
    `tabGL Entry`.creation ASC;

-- =================================================================
-- NOTES:
-- =================================================================
-- 1. This query supports all filters defined in the enhanced report
-- 2. Multi-select filters (account, party, project, cost_center) 
--    expect arrays/lists as input
-- 3. The balance calculation uses a subquery for running balance
-- 4. All optional filters check for NULL or empty string
-- 5. Party names are retrieved using COALESCE for different party types
-- 6. The query only returns submitted entries (docstatus = 1)
-- 7. Results are ordered by posting_date, account, and creation time
-- =================================================================

-- ALTERNATIVE QUERY FOR OPENING BALANCE:
-- =================================================================
-- Use this separate query to get opening balance before date range

SELECT
    'Opening Balance' AS 'account',
    SUM(`tabGL Entry`.debit) AS 'total_debit',
    SUM(`tabGL Entry`.credit) AS 'total_credit',
    (SUM(`tabGL Entry`.debit) - SUM(`tabGL Entry`.credit)) AS 'opening_balance'
FROM 
    `tabGL Entry`
WHERE 
    `tabGL Entry`.company = %(company)s
    AND `tabGL Entry`.posting_date < %(from_date)s
    AND `tabGL Entry`.docstatus = 1
    AND (
        %(account)s IS NULL 
        OR `tabGL Entry`.account IN %(account)s
    )
    -- Add other filters as needed
GROUP BY
    'Opening Balance';

-- =================================================================
-- QUERY FOR SUMMARY/TOTALS:
-- =================================================================

SELECT
    SUM(`tabGL Entry`.debit) AS 'total_debit',
    SUM(`tabGL Entry`.credit) AS 'total_credit',
    (SUM(`tabGL Entry`.debit) - SUM(`tabGL Entry`.credit)) AS 'net_balance',
    COUNT(DISTINCT `tabGL Entry`.voucher_no) AS 'total_vouchers',
    COUNT(`tabGL Entry`.name) AS 'total_entries'
FROM 
    `tabGL Entry`
WHERE 
    `tabGL Entry`.company = %(company)s
    AND `tabGL Entry`.posting_date BETWEEN %(from_date)s AND %(to_date)s
    AND `tabGL Entry`.docstatus = 1
    -- Add all filters same as main query
;

-- =================================================================
-- QUERY FOR MONTHLY AGGREGATION (for charts):
-- =================================================================

SELECT
    DATE_FORMAT(`tabGL Entry`.posting_date, '%Y-%m') AS 'month',
    DATE_FORMAT(`tabGL Entry`.posting_date, '%b %Y') AS 'month_label',
    SUM(`tabGL Entry`.debit) AS 'monthly_debit',
    SUM(`tabGL Entry`.credit) AS 'monthly_credit',
    (SUM(`tabGL Entry`.debit) - SUM(`tabGL Entry`.credit)) AS 'monthly_net'
FROM 
    `tabGL Entry`
WHERE 
    `tabGL Entry`.company = %(company)s
    AND `tabGL Entry`.posting_date BETWEEN %(from_date)s AND %(to_date)s
    AND `tabGL Entry`.docstatus = 1
    -- Add all filters same as main query
GROUP BY
    DATE_FORMAT(`tabGL Entry`.posting_date, '%Y-%m')
ORDER BY
    DATE_FORMAT(`tabGL Entry`.posting_date, '%Y-%m') ASC;

-- =================================================================
-- END OF SQL QUERIES
-- =================================================================
