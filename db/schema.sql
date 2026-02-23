PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- DEPARTMENTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS departments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    budget      REAL    NOT NULL DEFAULT 0.0,
    location    TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (DATE('now'))
);

-- ------------------------------------------------------------
-- ROLES / PERMISSIONS
-- permission_level:
--   1 = Read Only
--   2 = Standard User (add customers/orders)
--   3 = Supervisor (view all reports)
--   4 = Manager (financial reports)
--   5 = Admin (full access)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    name             TEXT    NOT NULL UNIQUE,
    permission_level INTEGER NOT NULL CHECK (permission_level BETWEEN 1 AND 5),
    description      TEXT
);

-- ------------------------------------------------------------
-- EMPLOYEES
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS employees (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name    TEXT    NOT NULL,
    last_name     TEXT    NOT NULL,
    email         TEXT    NOT NULL UNIQUE,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    role_id       INTEGER NOT NULL REFERENCES roles(id),
    hire_date     TEXT    NOT NULL,
    salary        REAL    NOT NULL DEFAULT 0.0,
    is_active     INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

-- ------------------------------------------------------------
-- CUSTOMERS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    phone       TEXT,
    region      TEXT    NOT NULL,
    created_at  TEXT    NOT NULL DEFAULT (DATETIME('now')),
    last_order  TEXT,
    is_active   INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

-- ------------------------------------------------------------
-- PRODUCTS
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS products (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    unit_price  REAL    NOT NULL CHECK (unit_price >= 0),
    stock_qty   INTEGER NOT NULL DEFAULT 0 CHECK (stock_qty >= 0),
    reorder_lvl INTEGER NOT NULL DEFAULT 10
);

-- ------------------------------------------------------------
-- ORDERS
-- status: pending | fulfilled | cancelled
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS orders (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id   INTEGER NOT NULL REFERENCES customers(id),
    employee_id   INTEGER NOT NULL REFERENCES employees(id),
    status        TEXT    NOT NULL DEFAULT 'pending'
                          CHECK (status IN ('pending', 'fulfilled', 'cancelled')),
    created_at    TEXT    NOT NULL DEFAULT (DATETIME('now')),
    fulfilled_at  TEXT,
    total_amount  REAL    NOT NULL DEFAULT 0.0
);

-- ------------------------------------------------------------
-- ORDER ITEMS  (line items linking orders to products)
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS order_items (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id    INTEGER NOT NULL REFERENCES orders(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    unit_price  REAL    NOT NULL  -- snapshot of price at time of order
);

-- ------------------------------------------------------------
-- INDEXES
-- ------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_orders_customer   ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_employee   ON orders(employee_id);
CREATE INDEX IF NOT EXISTS idx_orders_status     ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_created    ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_employees_dept    ON employees(department_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items(order_id);
