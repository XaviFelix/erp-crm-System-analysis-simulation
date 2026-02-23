PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- DEPARTMENTS
-- ------------------------------------------------------------
INSERT INTO departments (name, budget, location) VALUES
    ('Sales',           850000.00,  'New York'),
    ('Engineering',     1200000.00, 'Austin'),
    ('Customer Support',350000.00,  'Chicago'),
    ('Finance',         500000.00,  'New York'),
    ('Operations',      620000.00,  'Dallas');

-- ------------------------------------------------------------
-- ROLES
-- ------------------------------------------------------------
INSERT INTO roles (name, permission_level, description) VALUES
    ('Viewer',          1, 'Read-only access to basic records'),
    ('Sales Rep',       2, 'Can add customers and create orders'),
    ('Supervisor',      3, 'Can view all operational reports'),
    ('Manager',         4, 'Can access financial and HR reports'),
    ('Administrator',   5, 'Full system access');

-- ------------------------------------------------------------
-- EMPLOYEES
-- ------------------------------------------------------------
INSERT INTO employees (first_name, last_name, email, department_id, role_id, hire_date, salary, is_active) VALUES
    ('James',   'Carter',   'jcarter@erpsim.com',    1, 2, '2021-03-15', 68000,  1),
    ('Sofia',   'Nguyen',   'snguyen@erpsim.com',    1, 2, '2020-07-01', 72000,  1),
    ('Marcus',  'Webb',     'mwebb@erpsim.com',      1, 3, '2019-11-20', 91000,  1),
    ('Priya',   'Sharma',   'psharma@erpsim.com',    2, 2, '2022-01-10', 95000,  1),
    ('Leon',    'Fischer',  'lfischer@erpsim.com',   2, 3, '2018-06-05', 110000, 1),
    ('Dana',    'Brooks',   'dbrooks@erpsim.com',    3, 1, '2023-02-28', 52000,  1),
    ('Aaliya',  'Hassan',   'ahassan@erpsim.com',    3, 2, '2021-09-14', 58000,  1),
    ('Trevor',  'Kim',      'tkim@erpsim.com',       4, 4, '2017-04-22', 125000, 1),
    ('Renee',   'Alvarez',  'ralvarez@erpsim.com',   4, 3, '2020-12-01', 98000,  1),
    ('Omar',    'Jackson',  'ojackson@erpsim.com',   5, 5, '2016-08-30', 140000, 1),
    ('Claire',  'Wu',       'cwu@erpsim.com',        1, 2, '2022-05-17', 67000,  1),
    ('Derek',   'Patel',    'dpatel@erpsim.com',     2, 2, '2023-03-09', 89000,  0);  -- inactive employee

-- ------------------------------------------------------------
-- CUSTOMERS
-- ------------------------------------------------------------
INSERT INTO customers (name, email, phone, region, created_at, last_order, is_active) VALUES
    ('Apex Logistics',        'contact@apexlogistics.com',   '212-555-0101', 'Northeast', '2022-01-15', '2024-11-20', 1),
    ('Blue Ridge Retail',     'orders@blueridge.com',        '704-555-0182', 'Southeast', '2021-08-03', '2024-10-05', 1),
    ('CoreTech Solutions',    'billing@coretech.io',         '512-555-0245', 'Southwest', '2020-05-22', '2024-12-01', 1),
    ('Delta Supply Co.',      'purchasing@deltasupply.com',  '214-555-0317', 'South',     '2023-02-11', '2024-09-14', 1),
    ('Eastwood Enterprises',  'info@eastwoodent.com',        '617-555-0398', 'Northeast', '2019-11-30', '2024-07-22', 1),
    ('FrontLine Foods',       'ops@frontlinefoods.com',      '773-555-0421', 'Midwest',   '2022-06-07', '2023-10-01', 1),  -- will be inactive by query
    ('GridMark Industries',   'accounts@gridmark.biz',       '303-555-0513', 'West',      '2021-03-19', '2024-11-30', 1),
    ('Harbor Point Group',    'finance@harborpoint.com',     '206-555-0674', 'Northwest', '2023-07-25', '2024-12-10', 1),
    ('Ironside Manufacturing','buy@ironside.mfg',            '313-555-0756', 'Midwest',   '2020-09-08', '2023-08-15', 1),  -- inactive by query
    ('Jade Path Trading',     'trade@jadepath.com',          '415-555-0832', 'West',      '2022-12-01', '2024-12-05', 1),
    ('Keystone Partners',     'keystone@partners.net',       '215-555-0914', 'Northeast', '2021-04-14', '2024-06-30', 1),
    ('Luminary Tech',         'hello@luminarytech.com',      '512-555-1001', 'Southwest', '2023-09-18', '2024-11-11', 1),
    ('Metro Build Group',     'contracts@metrobuild.com',    '718-555-1123', 'Northeast', '2020-02-27', '2022-12-01', 0),  -- explicitly inactive
    ('NorthStar Wholesale',   'wholesale@northstar.com',     '612-555-1204', 'Midwest',   '2022-08-30', '2024-10-20', 1),
    ('Orion Health Systems',  'procurement@orionhealth.org', '404-555-1345', 'Southeast', '2021-06-15', '2024-12-08', 1);

-- ------------------------------------------------------------
-- PRODUCTS
-- ------------------------------------------------------------
INSERT INTO products (name, category, unit_price, stock_qty, reorder_lvl) VALUES
    ('Enterprise License - Basic',    'Software',  1200.00,  50,  5),
    ('Enterprise License - Pro',      'Software',  3500.00,  30,  5),
    ('Cloud Storage 1TB (annual)',     'Cloud',      480.00, 200, 20),
    ('Cloud Storage 5TB (annual)',     'Cloud',     1800.00, 120, 10),
    ('API Access Bundle',             'Software',   950.00,  75, 10),
    ('On-site Support (per day)',      'Services', 2200.00, 999,  0),  -- service, no reorder
    ('Training Session (per seat)',    'Services',  350.00, 999,  0),
    ('Hardware - Server Unit',        'Hardware', 12000.00,   8, 10),  -- LOW STOCK
    ('Hardware - Network Switch',     'Hardware',  2400.00,   6, 10),  -- LOW STOCK
    ('Maintenance Contract (annual)', 'Services',  1500.00, 999,  0),
    ('Data Analytics Module',         'Software',  4200.00,  22,  5),
    ('Security Audit Package',        'Services',  3800.00, 999,  0);

-- ------------------------------------------------------------
-- ORDERS
-- ------------------------------------------------------------

INSERT INTO orders (customer_id, employee_id, status, created_at, fulfilled_at, total_amount) VALUES
    -- November 2023
    (1,  1,  'fulfilled', '2023-11-05', '2023-11-07', 4700.00),
    (3,  2,  'fulfilled', '2023-11-12', '2023-11-14', 10500.00),
    (5,  3,  'fulfilled', '2023-11-20', '2023-11-22', 2400.00),
    -- December 2023
    (2,  1,  'fulfilled', '2023-12-03', '2023-12-05', 8200.00),
    (7,  2,  'fulfilled', '2023-12-10', '2023-12-12', 3500.00),
    (10, 11, 'fulfilled', '2023-12-18', '2023-12-20', 6300.00),
    -- January 2024
    (4,  1,  'fulfilled', '2024-01-08', '2024-01-10', 2200.00),
    (8,  3,  'fulfilled', '2024-01-15', '2024-01-17', 14400.00),
    (12, 2,  'fulfilled', '2024-01-22', '2024-01-24', 4800.00),
    (15, 11, 'fulfilled', '2024-01-29', '2024-01-31', 9500.00),
    -- February 2024
    (1,  2,  'fulfilled', '2024-02-06', '2024-02-08', 5600.00),
    (6,  1,  'fulfilled', '2024-02-14', '2024-02-16', 1800.00),
    (11, 3,  'fulfilled', '2024-02-21', '2024-02-23', 7200.00),
    -- March 2024
    (3,  11, 'fulfilled', '2024-03-04', '2024-03-06', 12600.00),
    (9,  2,  'fulfilled', '2024-03-11', '2024-03-13', 3800.00),
    (14, 1,  'fulfilled', '2024-03-19', '2024-03-21', 6000.00),
    (5,  3,  'fulfilled', '2024-03-26', '2024-03-28', 4200.00),
    -- April 2024
    (2,  2,  'fulfilled', '2024-04-02', '2024-04-04', 9100.00),
    (7,  11, 'fulfilled', '2024-04-09', '2024-04-11', 2400.00),
    (10, 1,  'fulfilled', '2024-04-16', '2024-04-18', 15000.00),
    -- May 2024
    (1,  3,  'fulfilled', '2024-05-07', '2024-05-09', 7600.00),
    (13, 2,  'cancelled', '2024-05-14', NULL,          0.00),
    (4,  1,  'fulfilled', '2024-05-21', '2024-05-23', 4500.00),
    (15, 11, 'fulfilled', '2024-05-28', '2024-05-30', 11200.00),
    -- June 2024
    (8,  2,  'fulfilled', '2024-06-04', '2024-06-06', 3800.00),
    (12, 3,  'fulfilled', '2024-06-11', '2024-06-13', 8400.00),
    (3,  1,  'fulfilled', '2024-06-18', '2024-06-20', 6200.00),
    -- July 2024
    (10, 11, 'fulfilled', '2024-07-02', '2024-07-04', 9800.00),
    (5,  2,  'fulfilled', '2024-07-09', '2024-07-11', 5200.00),
    (14, 3,  'fulfilled', '2024-07-16', '2024-07-18', 7100.00),
    (1,  1,  'fulfilled', '2024-07-23', '2024-07-25', 4300.00),
    -- August 2024
    (7,  2,  'fulfilled', '2024-08-06', '2024-08-08', 12000.00),
    (11, 3,  'fulfilled', '2024-08-13', '2024-08-15', 6800.00),
    (15, 1,  'fulfilled', '2024-08-20', '2024-08-22', 3500.00),
    -- September 2024
    (2,  11, 'fulfilled', '2024-09-03', '2024-09-05', 10200.00),
    (4,  2,  'fulfilled', '2024-09-10', '2024-09-12', 4700.00),
    (8,  3,  'fulfilled', '2024-09-17', '2024-09-19', 8900.00),
    (12, 1,  'fulfilled', '2024-09-24', '2024-09-26', 5100.00),
    -- October 2024
    (3,  2,  'fulfilled', '2024-10-01', '2024-10-03', 14800.00),
    (10, 11, 'fulfilled', '2024-10-08', '2024-10-10', 6400.00),
    (14, 3,  'fulfilled', '2024-10-15', '2024-10-17', 9200.00),
    (1,  1,  'fulfilled', '2024-10-22', '2024-10-24', 7800.00),
    -- November 2024
    (5,  2,  'fulfilled', '2024-11-05', '2024-11-07', 11500.00),
    (7,  3,  'fulfilled', '2024-11-12', '2024-11-14', 4900.00),
    (15, 1,  'fulfilled', '2024-11-19', '2024-11-21', 8100.00),
    (8,  11, 'fulfilled', '2024-11-26', '2024-11-28', 6700.00),
    -- December 2024
    (1,  2,  'fulfilled', '2024-12-03', '2024-12-05', 13200.00),
    (3,  3,  'fulfilled', '2024-12-10', '2024-12-12', 9400.00),
    (10, 1,  'fulfilled', '2024-12-17', '2024-12-19', 7300.00),
    (12, 11, 'pending',   '2024-12-24', NULL,          5800.00),
    (15, 2,  'pending',   '2024-12-28', NULL,          4100.00);

-- ------------------------------------------------------------
-- ORDER ITEMS
-- ------------------------------------------------------------
INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1,  1,  2, 1200.00), (1,  7,  2,  350.00),   -- order 1
    (2,  2,  3, 3500.00),                           -- order 2
    (3,  3,  5,  480.00),                           -- order 3
    (4,  11, 1, 4200.00), (4,  5,  2,  950.00), (4, 7, 4, 350.00), -- order 4
    (5,  1,  1, 1200.00), (5,  10, 1, 1500.00), (5, 3, 2, 480.00),  -- order 5
    (8,  8,  1,12000.00), (8,  9,  1, 2400.00),    -- order 8  (hardware)
    (10, 2,  2, 3500.00), (10, 10, 1, 1500.00), (10, 7, 3, 350.00), -- order 10
    (14, 2,  3, 3500.00), (14, 10, 1, 1500.00),    -- order 14
    (20, 8,  1,12000.00), (20, 9,  1, 2400.00), (20, 10, 1, 600.00), -- order 20
    (32, 8,  1,12000.00),                           -- order 32 (hardware)
    (39, 11, 3, 4200.00), (39, 5,  1,  950.00), (39, 10, 1, 1500.00), -- order 39
    (47, 2,  2, 3500.00), (47, 11, 1, 4200.00), (47, 7, 4, 350.00);  -- order 47
