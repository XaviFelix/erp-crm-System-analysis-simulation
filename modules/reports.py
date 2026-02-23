from db.database import get_connection

def _fetch(sql: str, params: tuple = ()) -> list:
    conn = get_connection()
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    conn.close()
    return rows


# ── Monthly Revenue ──────────────────────────────────────────────────

QUERY_MONTHLY_REVENUE = """
SELECT
    STRFTIME('%Y-%m', created_at)   AS month,
    COUNT(*)                        AS total_orders,
    SUM(total_amount)               AS revenue
FROM orders
WHERE status = 'fulfilled'
GROUP BY month
ORDER BY month DESC;
"""

def monthly_revenue():
    """Total fulfilled revenue grouped by calendar month."""
    return _fetch(QUERY_MONTHLY_REVENUE)


# ── Revenue by Department ───────────────────────────────────────────

QUERY_REVENUE_BY_DEPARTMENT = """
SELECT
    d.name                          AS department,
    COUNT(o.id)                     AS orders_processed,
    SUM(o.total_amount)             AS total_revenue,
    ROUND(AVG(o.total_amount), 2)   AS avg_order_value
FROM orders o
JOIN employees e ON o.employee_id = e.id
JOIN departments d ON e.department_id = d.id
WHERE o.status = 'fulfilled'
GROUP BY d.name
ORDER BY total_revenue DESC;
"""

def revenue_by_department():
    """Which departments are driving the most fulfilled revenue."""
    return _fetch(QUERY_REVENUE_BY_DEPARTMENT)


# ── Top 5 Customers by Spend ────────────────────────────────────────

QUERY_TOP_CUSTOMERS = """
SELECT
    c.name                          AS customer,
    c.region,
    COUNT(o.id)                     AS total_orders,
    SUM(o.total_amount)             AS lifetime_spend,
    MAX(o.created_at)               AS last_order_date
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE o.status = 'fulfilled'
GROUP BY c.id
ORDER BY lifetime_spend DESC
LIMIT 5;
"""

def top_customers():
    """Top 5 customers ranked by total lifetime spend."""
    return _fetch(QUERY_TOP_CUSTOMERS)


# ── Inactive Customer Accounts (90+ days no order) ──────────────────

QUERY_INACTIVE_CUSTOMERS = """
SELECT
    c.name                                              AS customer,
    c.email,
    c.region,
    c.last_order,
    CAST(JULIANDAY('now') - JULIANDAY(c.last_order)
         AS INTEGER)                                    AS days_since_order,
    CASE WHEN c.is_active = 1 THEN 'Active'
         ELSE 'Deactivated' END                         AS account_status
FROM customers c
WHERE c.last_order IS NULL
   OR JULIANDAY('now') - JULIANDAY(c.last_order) > 90
ORDER BY days_since_order DESC;
"""

def inactive_customers():
    """Customers with no order activity in the last 90+ days."""
    return _fetch(QUERY_INACTIVE_CUSTOMERS)


# ── Employee Order Performance ──────────────────────────────────────

QUERY_EMPLOYEE_PERFORMANCE = """
SELECT
    e.first_name || ' ' || e.last_name  AS employee,
    d.name                              AS department,
    r.name                              AS role,
    COUNT(o.id)                         AS orders_handled,
    SUM(o.total_amount)                 AS total_value,
    ROUND(AVG(o.total_amount), 2)       AS avg_order_value
FROM employees e
JOIN departments d ON e.department_id = d.id
JOIN roles r ON e.role_id = r.id
LEFT JOIN orders o ON o.employee_id = e.id AND o.status = 'fulfilled'
WHERE e.is_active = 1
GROUP BY e.id
ORDER BY orders_handled DESC;
"""

def employee_performance():
    """How many orders and total value each active employee has processed."""
    return _fetch(QUERY_EMPLOYEE_PERFORMANCE)


# ── Low Stock Product Alert ─────────────────────────────────────────

QUERY_LOW_STOCK = """
SELECT
    name                            AS product,
    category,
    stock_qty                       AS current_stock,
    reorder_lvl                     AS reorder_level,
    reorder_lvl - stock_qty         AS units_below_threshold,
    unit_price
FROM products
WHERE stock_qty < reorder_lvl
  AND reorder_lvl > 0              -- exclude service items
ORDER BY units_below_threshold DESC;
"""

def low_stock_alert():
    """Products whose stock quantity is below their reorder threshold."""
    return _fetch(QUERY_LOW_STOCK)


# ── Orders by Status ─────────────────────────────────────────────────

QUERY_ORDERS_BY_STATUS = """
SELECT
    status,
    COUNT(*)                        AS order_count,
    SUM(total_amount)               AS total_value,
    ROUND(AVG(total_amount), 2)     AS avg_value,
    MIN(created_at)                 AS earliest,
    MAX(created_at)                 AS latest
FROM orders
GROUP BY status
ORDER BY order_count DESC;
"""

def orders_by_status():
    """Breakdown of all orders grouped by fulfillment status."""
    return _fetch(QUERY_ORDERS_BY_STATUS)


# ── Average Order Value by Region ────────────────────────────────────

QUERY_AOV_BY_REGION = """
SELECT
    c.region,
    COUNT(o.id)                     AS total_orders,
    SUM(o.total_amount)             AS total_revenue,
    ROUND(AVG(o.total_amount), 2)   AS avg_order_value,
    MAX(o.total_amount)             AS largest_order
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.status = 'fulfilled'
GROUP BY c.region
ORDER BY total_revenue DESC;
"""

def aov_by_region():
    """Average order value and total revenue broken down by customer region."""
    return _fetch(QUERY_AOV_BY_REGION)


# ── Department Headcount & Average Salary ───────────────────────────

QUERY_DEPT_HEADCOUNT = """
SELECT
    d.name                          AS department,
    d.location,
    d.budget                        AS dept_budget,
    COUNT(e.id)                     AS headcount,
    ROUND(AVG(e.salary), 2)         AS avg_salary,
    SUM(e.salary)                   AS total_payroll,
    ROUND(SUM(e.salary) / d.budget * 100, 1)
                                    AS payroll_pct_of_budget
FROM departments d
LEFT JOIN employees e ON e.department_id = d.id AND e.is_active = 1
GROUP BY d.id
ORDER BY headcount DESC;
"""

def dept_headcount():
    """Headcount, salary averages, and payroll as a % of department budget."""
    return _fetch(QUERY_DEPT_HEADCOUNT)


# ── Role-Based Access Audit ────────────────────────────────────────

QUERY_ACCESS_AUDIT = """
SELECT
    e.first_name || ' ' || e.last_name  AS employee,
    e.email,
    d.name                              AS department,
    r.name                              AS role,
    r.permission_level,
    r.description                       AS access_scope,
    CASE WHEN e.is_active = 1 THEN 'Active'
         ELSE 'Inactive' END            AS account_status
FROM employees e
JOIN roles r ON e.role_id = r.id
JOIN departments d ON e.department_id = d.id
WHERE r.permission_level >= 4
ORDER BY r.permission_level DESC, d.name;
"""

def access_audit():
    """Employees with elevated permissions (level 4–5) for security review."""
    return _fetch(QUERY_ACCESS_AUDIT)


# ── Query Registry (used by CLI menu) ────────────────────────────────────────

REPORT_MENU = [
    ("Monthly Revenue",                monthly_revenue),
    ("Revenue by Department",          revenue_by_department),
    ("Top 5 Customers by Spend",       top_customers),
    ("Inactive Customer Accounts",     inactive_customers),
    ("Employee Order Performance",     employee_performance),
    ("Low Stock Product Alert",        low_stock_alert),
    ("Orders by Status",               orders_by_status),
    ("Avg Order Value by Region",      aov_by_region),
    ("Department Headcount & Salary",  dept_headcount),
    ("Role-Based Access Audit",        access_audit),
]
