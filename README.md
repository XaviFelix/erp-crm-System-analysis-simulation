# ERP Simulation System

This system simulates the key modules and concepts found in ERP platforms such as:
- employee and department management
- customer relationship tracking
- order processing
- inventory control
- and role-based access

> CRM workflow layer in progress

---

## Database Schema

Normalized tables modeling a real ERP data structure:

**Referential integrity** is enforced via foreign key constraints. **Role-based access** is enforced at both the application and query level.

---

## Business Queries

- Monthly Revenue
- Revenue by Department
- Top 5 Customers by Spend
- Inactive Customer Accounts
- Employee Order Performance
- Low Stock Product Alert
- Orders by Status
- Avg Order Value by Region
- Department Headcount & Salary
- Role-Based Access Audit

---

## Features

**Role-Based Access Control** — Five permission tiers.Menu options are physically hidden from users who lack access

**Transactional Order Processing** — Orders commit in a single transaction. Rolled back automatically on failure.

**Duplicate Prevention** — Case-insensitive email uniqueness enforced at the database level

---

## Documents

- Business Requirements Document — functional requirements, data model, access matrix, UAT overview
- UAT Log — 10 test cases

---

## Tech Stack

Language: Python
Database: SQLite
Interface: CLI
