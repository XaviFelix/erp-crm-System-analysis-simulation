import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from db.database import get_connection
from modules.auth import (
    require_permission, print_header, ok, err, warn,
    pause, divider, get_str_input, get_choice, C
)

REGIONS = ["northeast", "southeast", "south", "midwest", "southwest", "west", "northwest"]


# ── Table Printer ─────────────────────────────────────────────

def _print_customer_table(rows):
    if not rows:
        warn("No customers found.")
        return

    # Column widths
    W = {"id": 5, "name": 26, "email": 30, "region": 11, "last_order": 12, "status": 10}

    def col(val, width):
        s = str(val or "—")
        return s[:width].ljust(width)

    # Header
    print(C.BOLD)
    print(
        f"  {'ID':<{W['id']}}  "
        f"{'NAME':<{W['name']}}  "
        f"{'EMAIL':<{W['email']}}  "
        f"{'REGION':<{W['region']}}  "
        f"{'LAST ORDER':<{W['last_order']}}  "
        f"{'STATUS':<{W['status']}}"
    )
    print(C.RESET, end="")
    divider()

    for row in rows:
        status     = "Active" if row["is_active"] else "Inactive"
        status_clr = C.GREEN if row["is_active"] else C.RED
        print(
            f"  {col(row['id'],         W['id'])}  "
            f"{col(row['name'],        W['name'])}  "
            f"{col(row['email'],       W['email'])}  "
            f"{col(row['region'],      W['region'])}  "
            f"{col(row['last_order'],  W['last_order'])}  "
            f"{status_clr}{status:<{W['status']}}{C.RESET}"
        )

    divider()
    print(f"  {C.DIM}{len(rows)} record(s) returned.{C.RESET}\n")


# ── Add Customer ──────────────────────────────────────────────

def add_customer(session: dict):
    if not require_permission(session, 2, "Add Customer"):
        pause()
        return

    print_header(session)
    print(f"  {C.BOLD}Add New Customer{C.RESET}")
    print(f"  {C.DIM}Enter '0' at any prompt to cancel.{C.RESET}\n")
    divider()

    # --- Name ---
    name = get_str_input("Customer / Company Name : ")
    if name is None:
        warn("Cancelled.")
        pause()
        return

    # --- Email ---
    while True:
        email = get_str_input("Email Address          : ")
        if email is None:
            warn("Cancelled.")
            pause()
            return
        # Basic format check
        if "@" not in email or "." not in email.split("@")[-1]:
            err("Please enter a valid email address.")
            continue
        # Duplicate check
        conn = get_connection()
        exists = conn.execute(
            "SELECT id FROM customers WHERE LOWER(email) = LOWER(?)", (email,)
        ).fetchone()
        conn.close()
        if exists:
            err(f"A customer with email '{email}' already exists (ID {exists['id']}).")
            continue
        break

    # --- Phone ---
    phone = get_str_input("Phone (optional, Enter to skip) : ", allow_blank=True)
    if phone is None:
        warn("Cancelled.")
        pause()
        return
    phone = phone or None

    # --- Region ---
    print(f"\n  Regions: {', '.join(r.title() for r in REGIONS)}")
    while True:
        region_raw = get_str_input("Region                 : ")
        if region_raw is None:
            warn("Cancelled.")
            pause()
            return
        if region_raw.lower() not in REGIONS:
            err(f"Invalid region. Choose from: {', '.join(r.title() for r in REGIONS)}")
            continue
        region = region_raw.title()
        break

    # --- Confirm ---
    print()
    divider()
    print(f"  {C.BOLD}Review before saving:{C.RESET}")
    print(f"    Name   : {name}")
    print(f"    Email  : {email}")
    print(f"    Phone  : {phone or '(none)'}")
    print(f"    Region : {region}")
    divider()

    confirm = get_choice("Save this customer? [y/n]: ", ["y", "n"])
    if confirm != "y":
        warn("Cancelled — customer not saved.")
        pause()
        return

    # --- Insert ---
    conn = get_connection()
    cur = conn.execute(
        """
        INSERT INTO customers (name, email, phone, region, is_active)
        VALUES (?, ?, ?, ?, 1)
        """,
        (name, email, phone, region)
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    ok(f"Customer '{name}' added successfully! (ID {new_id})")
    pause()


# ── View Customers ────────────────────────────────────────────

def view_customers(session: dict):
    if not require_permission(session, 1, "View Customers"):
        pause()
        return

    print_header(session)
    print(f"  {C.BOLD}Customer List{C.RESET}")
    print(f"  {C.DIM}Filter by status below. Enter '0' to go back.{C.RESET}\n")
    divider()
    print("  [1] Active customers only")
    print("  [2] Inactive customers only")
    print("  [3] All customers")
    print("  [0] Back")
    divider()

    choice = get_choice("Select filter: ", ["1", "2", "3", "0"])
    if not choice or choice == "0":
        return

    if choice == "1":
        where, label = "WHERE is_active = 1", "Active Customers"
    elif choice == "2":
        where, label = "WHERE is_active = 0", "Inactive Customers"
    else:
        where, label = "", "All Customers"

    conn = get_connection()
    rows = conn.execute(f"""
        SELECT id, name, email, region, last_order, is_active
        FROM customers
        {where}
        ORDER BY name ASC
    """).fetchall()
    conn.close()

    print()
    print(f"  {C.BOLD}{label}{C.RESET}\n")
    _print_customer_table(rows)
    pause()


# ── Search Customer ───────────────────────────────────────────

def search_customer(session: dict):
    if not require_permission(session, 1, "Search Customers"):
        pause()
        return

    print_header(session)
    print(f"  {C.BOLD}Search Customers{C.RESET}")
    print(f"  {C.DIM}Search by name or email. Enter '0' to cancel.{C.RESET}\n")
    divider()

    term = get_str_input("Search term : ")
    if term is None:
        return

    conn = get_connection()
    rows = conn.execute("""
        SELECT id, name, email, region, last_order, is_active
        FROM customers
        WHERE LOWER(name)  LIKE LOWER(?)
           OR LOWER(email) LIKE LOWER(?)
        ORDER BY name ASC
    """, (f"%{term}%", f"%{term}%")).fetchall()
    conn.close()

    print()
    if not rows:
        warn(f"No customers found matching '{term}'.")
    else:
        print(f"  {C.BOLD}Results for \"{term}\"{C.RESET}\n")
        _print_customer_table(rows)

    pause()


# ── Customer Menu ─────────────────────────────────────────────

def customer_menu(session: dict):
    while True:
        print_header(session)
        print(f"  {C.BOLD}Customer Management{C.RESET}\n")
        divider()
        print("  [1] View Customers")
        print("  [2] Search Customer")
        if session["level"] >= 2:
            print("  [3] Add New Customer")
        print("  [0] Back to Main Menu")
        divider()

        options = ["1", "2", "0"] + (["3"] if session["level"] >= 2 else [])
        choice = get_choice("Select option: ", options)

        if not choice or choice == "0":
            return
        elif choice == "1":
            view_customers(session)
        elif choice == "2":
            search_customer(session)
        elif choice == "3":
            add_customer(session)
