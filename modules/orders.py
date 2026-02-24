import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from db.database import get_connection
from modules.auth import (
    require_permission, print_header, ok, err, warn,
    pause, divider, get_str_input, get_int_input, get_choice, C
)


# ── Table Printers ────────────────────────────────────────────

def _print_order_table(rows):
    if not rows:
        warn("No orders found.")
        return

    W = {"id": 5, "customer": 24, "employee": 20, "status": 11, "created": 12, "total": 12}

    def col(val, width):
        return str(val or "—")[:width].ljust(width)

    def status_color(s):
        return {
            "fulfilled": C.GREEN,
            "pending":   C.YELLOW,
            "cancelled": C.RED,
        }.get(s, C.RESET)

    print(C.BOLD)
    print(
        f"  {'ID':<{W['id']}}  "
        f"{'CUSTOMER':<{W['customer']}}  "
        f"{'PROCESSED BY':<{W['employee']}}  "
        f"{'STATUS':<{W['status']}}  "
        f"{'DATE':<{W['created']}}  "
        f"{'TOTAL':>{W['total']}}"
    )
    print(C.RESET, end="")
    divider()

    for row in rows:
        sc = status_color(row["status"])
        total = f"${row['total_amount']:,.2f}" if row["total_amount"] else "—"
        print(
            f"  {col(row['id'],           W['id'])}  "
            f"{col(row['customer'],      W['customer'])}  "
            f"{col(row['employee'],      W['employee'])}  "
            f"{sc}{col(row['status'], W['status'])}{C.RESET}  "
            f"{col(row['created_at'][:10], W['created'])}  "
            f"{total:>{W['total']}}"
        )

    divider()
    print(f"  {C.DIM}{len(rows)} record(s) returned.{C.RESET}\n")


def _print_line_items(items):
    if not items:
        return
    print(f"\n  {C.BOLD}Line Items:{C.RESET}")
    divider("─", 55)
    print(f"  {'PRODUCT':<34}  {'QTY':>4}  {'UNIT PRICE':>11}  {'SUBTOTAL':>11}")
    divider("─", 55)
    for item in items:
        subtotal = item["quantity"] * item["unit_price"]
        print(
            f"  {str(item['product'])[:34]:<34}  "
            f"{item['quantity']:>4}  "
            f"${item['unit_price']:>10,.2f}  "
            f"${subtotal:>10,.2f}"
        )
    divider("─", 55)


def _print_product_catalog(products):
    print(f"\n  {C.BOLD}Available Products:{C.RESET}")
    divider("─", 62)
    print(f"  {'ID':<5}  {'PRODUCT':<34}  {'CATEGORY':<12}  {'PRICE':>10}  {'STOCK':>6}")
    divider("─", 62)
    for p in products:
        stock_clr = C.RED if p["stock_qty"] < p["reorder_lvl"] and p["reorder_lvl"] > 0 else C.RESET
        print(
            f"  {p['id']:<5}  "
            f"{str(p['name'])[:34]:<34}  "
            f"{str(p['category'])[:12]:<12}  "
            f"${p['unit_price']:>9,.2f}  "
            f"{stock_clr}{p['stock_qty']:>6}{C.RESET}"
        )
    divider("─", 62)
    print(f"  {C.DIM}* Red stock = below reorder threshold{C.RESET}\n")


# ── Create the Order ──────────────────────────────────────────────

def create_order(session: dict):
    if not require_permission(session, 2, "Create Order"):
        pause()
        return

    print_header(session)
    print(f"  {C.BOLD}Create New Order{C.RESET}")
    print(f"  {C.DIM}Enter '0' at any prompt to cancel.{C.RESET}\n")
    divider()

    # ── Select Customer ───────────────────────────────
    print(f"\n  {C.BOLD}Step 1 of 3 — Select Customer{C.RESET}")
    print(f"  {C.DIM}Search by name or email to find the customer.{C.RESET}\n")

    customer = None
    while customer is None:
        term = get_str_input("Customer search : ")
        if term is None:
            warn("Order creation cancelled.")
            pause()
            return

        conn = get_connection()
        results = conn.execute("""
            SELECT id, name, email, region
            FROM customers
            WHERE is_active = 1
              AND (LOWER(name) LIKE LOWER(?) OR LOWER(email) LIKE LOWER(?))
            ORDER BY name
        """, (f"%{term}%", f"%{term}%")).fetchall()
        conn.close()

        if not results:
            warn(f"No active customers found matching '{term}'. Try again.")
            continue

        if len(results) == 1:
            customer = results[0]
            ok(f"Customer selected: {customer['name']} ({customer['email']})")
        else:
            print(f"\n  {C.BOLD}Multiple matches — select one:{C.RESET}\n")
            for i, r in enumerate(results, 1):
                print(f"  [{i}] {r['name']}  —  {r['email']}  ({r['region']})")
            print()
            idx = get_int_input("Enter number (0 to search again): ", min_val=1, max_val=len(results))
            if idx is None:
                continue
            customer = results[idx - 1]
            ok(f"Customer selected: {customer['name']}")

    print(f"\n  {C.BOLD}Step 2 of 3 — Add Line Items{C.RESET}")
    print(f"  {C.DIM}Add products to the order. Enter product ID and quantity.{C.RESET}")
    print(f"  {C.DIM}Type '0' when done adding items.{C.RESET}\n")

    conn = get_connection()
    products = conn.execute("""
        SELECT id, name, category, unit_price, stock_qty, reorder_lvl
        FROM products
        ORDER BY category, name
    """).fetchall()
    conn.close()

    _print_product_catalog(products)
    product_map = {p["id"]: p for p in products}

    line_items = []   # list of dicts: {product_id, name, quantity, unit_price}

    while True:
        # Show running cart
        if line_items:
            running_total = sum(i["quantity"] * i["unit_price"] for i in line_items)
            print(f"  {C.CYAN}Cart ({len(line_items)} item(s))  —  Running total: ${running_total:,.2f}{C.RESET}")
            _print_line_items(line_items)

        print(f"  {C.DIM}Enter product ID to add, or 0 to finish.{C.RESET}")
        prod_id = get_int_input("Product ID : ", min_val=1)

        if prod_id is None:
            if not line_items:
                err("An order must have at least one line item.")
                continue
            break

        if prod_id not in product_map:
            err(f"No product found with ID {prod_id}.")
            continue

        product = product_map[prod_id]

        # Check if already in cart
        existing = next((i for i in line_items if i["product_id"] == prod_id), None)
        if existing:
            warn(f"'{product['name']}' is already in the cart (qty: {existing['quantity']}).")
            qty = get_int_input("New quantity (0 to remove): ", min_val=0)
            if qty is None or qty == 0:
                line_items = [i for i in line_items if i["product_id"] != prod_id]
                ok(f"Removed '{product['name']}' from cart.")
            else:
                existing["quantity"] = qty
                ok(f"Updated '{product['name']}' quantity to {qty}.")
            continue

        qty = get_int_input(f"Quantity for '{product['name']}': ", min_val=1)
        if qty is None:
            continue

        # Warn on low stock
        if product["reorder_lvl"] > 0 and qty > product["stock_qty"]:
            warn(
                f"Requested qty ({qty}) exceeds current stock ({product['stock_qty']}). "
                "Adding anyway — inventory team will be notified."
            )

        line_items.append({
            "product_id": prod_id,
            "name":       product["name"],
            "quantity":   qty,
            "unit_price": product["unit_price"],
        })
        ok(f"Added: {product['name']}  x{qty}  @ ${product['unit_price']:,.2f}")

    # ── Review & Confirm ──────────────────────────────
    print(f"\n  {C.BOLD}Step 3 of 3 — Review & Confirm{C.RESET}\n")
    divider()
    print(f"  Customer  : {C.CYAN}{customer['name']}{C.RESET}  ({customer['region']})")
    print(f"  Processed : {session['name']}  ({session['role']})")
    print(f"  Status    : pending")

    total_amount = sum(i["quantity"] * i["unit_price"] for i in line_items)
    _print_line_items(line_items)
    print(f"\n  {C.BOLD}Order Total: {C.GREEN}${total_amount:,.2f}{C.RESET}")
    divider()

    confirm = get_choice("Submit this order? [y/n]: ", ["y", "n"])
    if confirm != "y":
        warn("Order cancelled — nothing was saved.")
        pause()
        return

    # ── Commit Transaction ────────────────────────────────────
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    try:
        cur = conn.execute("""
            INSERT INTO orders (customer_id, employee_id, status, created_at, total_amount)
            VALUES (?, ?, 'pending', ?, ?)
        """, (customer["id"], session["id"], now, total_amount))
        order_id = cur.lastrowid

        for item in line_items:
            conn.execute("""
                INSERT INTO order_items (order_id, product_id, quantity, unit_price)
                VALUES (?, ?, ?, ?)
            """, (order_id, item["product_id"], item["quantity"], item["unit_price"]))

            # Decrement stock for physical products
            conn.execute("""
                UPDATE products
                SET stock_qty = MAX(0, stock_qty - ?)
                WHERE id = ? AND reorder_lvl > 0
            """, (item["quantity"], item["product_id"]))

        # Update customer last_order timestamp
        conn.execute("""
            UPDATE customers SET last_order = ? WHERE id = ?
        """, (now[:10], customer["id"]))

        conn.commit()
        ok(f"Order #{order_id} created successfully! Total: ${total_amount:,.2f}")

    except Exception as e:
        conn.rollback()
        err(f"Transaction failed and was rolled back. Detail: {e}")
    finally:
        conn.close()

    pause()


# ── View Orders ───────────────────────────────────────────────

def view_orders(session: dict):
    if not require_permission(session, 1, "View Orders"):
        pause()
        return

    print_header(session)
    print(f"  {C.BOLD}View Orders{C.RESET}\n")
    divider()
    print("  [1] All orders")
    print("  [2] Pending only")
    print("  [3] Fulfilled only")
    print("  [4] Cancelled only")
    print("  [5] Lookup order by ID")
    print("  [0] Back")
    divider()

    choice = get_choice("Select filter: ", ["1", "2", "3", "4", "5", "0"])
    if not choice or choice == "0":
        return

    if choice == "5":
        _view_order_detail(session)
        return

    filters = {"1": ("", "All Orders"),
               "2": ("WHERE o.status = 'pending'",   "Pending Orders"),
               "3": ("WHERE o.status = 'fulfilled'", "Fulfilled Orders"),
               "4": ("WHERE o.status = 'cancelled'", "Cancelled Orders")}
    where, label = filters[choice]

    conn = get_connection()
    rows = conn.execute(f"""
        SELECT
            o.id,
            c.name  AS customer,
            e.first_name || ' ' || e.last_name AS employee,
            o.status,
            o.created_at,
            o.total_amount
        FROM orders o
        JOIN customers c  ON o.customer_id  = c.id
        JOIN employees e  ON o.employee_id  = e.id
        {where}
        ORDER BY o.created_at DESC
    """).fetchall()
    conn.close()

    print()
    print(f"  {C.BOLD}{label}{C.RESET}\n")
    _print_order_table(rows)
    pause()


def _view_order_detail(session: dict):
    print()
    order_id = get_int_input("Enter Order ID: ", min_val=1)
    if order_id is None:
        return

    conn = get_connection()
    order = conn.execute("""
        SELECT
            o.id,
            c.name  AS customer,
            c.region,
            e.first_name || ' ' || e.last_name AS employee,
            o.status,
            o.created_at,
            o.fulfilled_at,
            o.total_amount
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        JOIN employees e ON o.employee_id = e.id
        WHERE o.id = ?
    """, (order_id,)).fetchone()

    if not order:
        conn.close()
        err(f"No order found with ID {order_id}.")
        pause()
        return

    items = conn.execute("""
        SELECT p.name AS product, oi.quantity, oi.unit_price
        FROM order_items oi
        JOIN products p ON oi.product_id = p.id
        WHERE oi.order_id = ?
    """, (order_id,)).fetchall()
    conn.close()

    sc = {"fulfilled": C.GREEN, "pending": C.YELLOW, "cancelled": C.RED}.get(order["status"], C.RESET)
    print()
    divider()
    print(f"  {C.BOLD}Order #{order['id']}{C.RESET}")
    divider()
    print(f"  Customer     : {order['customer']}  ({order['region']})")
    print(f"  Processed by : {order['employee']}")
    print(f"  Status       : {sc}{order['status'].upper()}{C.RESET}")
    print(f"  Created      : {order['created_at']}")
    if order["fulfilled_at"]:
        print(f"  Fulfilled    : {order['fulfilled_at']}")
    _print_line_items(items)
    print(f"  {C.BOLD}Total: {C.GREEN}${order['total_amount']:,.2f}{C.RESET}")
    divider()
    pause()


# ── Update Order Status ───────────────────────────────────────

def update_order_status(session: dict):
    if not require_permission(session, 2, "Update Order Status"):
        pause()
        return

    print_header(session)
    print(f"  {C.BOLD}Update Order Status{C.RESET}")
    print(f"  {C.DIM}Enter '0' to cancel.{C.RESET}\n")
    divider()

    order_id = get_int_input("Order ID to update: ", min_val=1)
    if order_id is None:
        return

    conn = get_connection()
    order = conn.execute("""
        SELECT o.id, c.name AS customer, o.status, o.total_amount
        FROM orders o
        JOIN customers c ON o.customer_id = c.id
        WHERE o.id = ?
    """, (order_id,)).fetchone()
    conn.close()

    if not order:
        err(f"No order found with ID {order_id}.")
        pause()
        return

    sc = {"fulfilled": C.GREEN, "pending": C.YELLOW, "cancelled": C.RED}.get(order["status"], C.RESET)
    print(f"\n  Order #{order['id']}  —  {order['customer']}")
    print(f"  Current status : {sc}{order['status'].upper()}{C.RESET}")
    print(f"  Total          : ${order['total_amount']:,.2f}\n")

    if order["status"] == "fulfilled":
        warn("This order is already fulfilled and cannot be changed.")
        pause()
        return

    print("  New status options:")
    options = []
    if order["status"] == "pending":
        print("  [1] Mark as Fulfilled")
        print("  [2] Mark as Cancelled")
        options = ["1", "2", "0"]
    elif order["status"] == "cancelled":
        print("  [1] Reopen as Pending")
        options = ["1", "0"]
    print("  [0] Cancel (no change)")
    divider()

    choice = get_choice("Select: ", options)
    if not choice or choice == "0":
        warn("No changes made.")
        pause()
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if order["status"] == "pending" and choice == "1":
        new_status, fulfilled_at = "fulfilled", now
    elif order["status"] == "pending" and choice == "2":
        new_status, fulfilled_at = "cancelled", None
    else:
        new_status, fulfilled_at = "pending", None

    conn = get_connection()
    try:
        conn.execute("""
            UPDATE orders
            SET status = ?, fulfilled_at = ?
            WHERE id = ?
        """, (new_status, fulfilled_at, order_id))
        conn.commit()
        ok(f"Order #{order_id} status updated to '{new_status.upper()}'.")
    except Exception as e:
        conn.rollback()
        err(f"Update failed: {e}")
    finally:
        conn.close()

    pause()


# ── Orders Menu ───────────────────────────────────────────────

def orders_menu(session: dict):
    while True:
        print_header(session)
        print(f"  {C.BOLD}Order Processing{C.RESET}\n")
        divider()
        print("  [1] View Orders")
        if session["level"] >= 2:
            print("  [2] Create New Order")
            print("  [3] Update Order Status")
        print("  [0] Back to Main Menu")
        divider()

        options = ["1", "0"] + (["2", "3"] if session["level"] >= 2 else [])
        choice = get_choice("Select option: ", options)

        if not choice or choice == "0":
            return
        elif choice == "1":
            view_orders(session)
        elif choice == "2":
            create_order(session)
        elif choice == "3":
            update_order_status(session)
