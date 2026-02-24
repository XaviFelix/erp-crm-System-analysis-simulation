import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db.database import initialize_db
from modules.auth import (
    login, print_banner, print_header,
    require_permission, ok, err, warn,
    pause, divider, get_choice, C
)
from modules.customers  import customer_menu
from modules.orders     import orders_menu
from modules.reports_menu import reports_menu


# ── Admin Tools (Level 5) ────────────────────────────────

def admin_menu(session: dict):
    if not require_permission(session, 5, "Admin Tools"):
        pause()
        return

    while True:
        print_header(session)
        print(f"  {C.BOLD}{C.RED}Admin Tools{C.RESET}  —  Restricted Access\n")
        divider()
        print("  [1] Reset & Reseed Database")
        print("  [2] View All Employees")
        print("  [0] Back to Main Menu")
        divider()

        choice = get_choice("Select option: ", ["1", "2", "0"])

        if not choice or choice == "0":
            return

        elif choice == "1":
            print()
            warn("This will DELETE all data and reseed from scratch.")
            confirm = get_choice("Are you sure? Type 'yes' to confirm: ", ["yes", "no", "0"])
            if confirm == "yes":
                from db.database import reset_db
                reset_db()
                ok("Database reset and reseeded successfully.")
            else:
                warn("Reset cancelled.")
            pause()

        elif choice == "2":
            from db.database import get_connection
            conn = get_connection()
            rows = conn.execute("""
                SELECT
                    e.id,
                    e.first_name || ' ' || e.last_name AS name,
                    d.name  AS department,
                    r.name  AS role,
                    r.permission_level AS level,
                    CASE WHEN e.is_active = 1 THEN 'Active' ELSE 'Inactive' END AS status
                FROM employees e
                JOIN departments d ON e.department_id = d.id
                JOIN roles r       ON e.role_id       = r.id
                ORDER BY r.permission_level DESC, d.name
            """).fetchall()
            conn.close()

            print()
            print(f"  {C.BOLD}All Employees — Use ID to log in{C.RESET}\n")
            divider()
            print(f"  {'ID':<5}  {'NAME':<22}  {'DEPARTMENT':<18}  {'ROLE':<16}  {'LVL':<5}  STATUS")
            divider()
            for row in rows:
                sc = C.GREEN if row["status"] == "Active" else C.RED
                print(
                    f"  {row['id']:<5}  "
                    f"{str(row['name'])[:22]:<22}  "
                    f"{str(row['department'])[:18]:<18}  "
                    f"{str(row['role'])[:16]:<16}  "
                    f"{row['level']:<5}  "
                    f"{sc}{row['status']}{C.RESET}"
                )
            divider()
            pause()


# ── Main Menu ─────────────────────────────────────────────────

def main_menu(session: dict):
    while True:
        print_header(session)
        print(f"  {C.BOLD}Main Menu{C.RESET}\n")
        divider()

        # Always visible
        print("  [1] Customer Management")
        print("  [2] Order Processing")

        # Reports: Level 3+
        if session["level"] >= 3:
            print("  [3] Business Reports")
        else:
            print(f"  {C.DIM}[3] Business Reports  {C.YELLOW}[Level 3+]{C.RESET}")

        # Admin: Level 5 only
        if session["level"] >= 5:
            print(f"  {C.RED}[4] Admin Tools{C.RESET}")

        print()
        print("  [0] Logout")
        divider()

        valid = ["1", "2", "0"]
        if session["level"] >= 3:
            valid.append("3")
        if session["level"] >= 5:
            valid.append("4")

        choice = get_choice("Select option: ", valid)

        if not choice or choice == "0":
            return "logout"
        elif choice == "1":
            customer_menu(session)
        elif choice == "2":
            orders_menu(session)
        elif choice == "3":
            reports_menu(session)
        elif choice == "4":
            admin_menu(session)


# ── Application Bootstrap ─────────────────────────────────────

def main():
    # Ensure DB exists and is seeded on first run
    initialize_db(seed=True)

    while True:
        session = login()
        if session is None:
            break

        result = main_menu(session)

        if result == "logout":
            print_banner()
            print(f"  {C.DIM}You have been logged out.{C.RESET}")
            print(f"  {C.DIM}Press Ctrl+C to exit or Enter to log in again.{C.RESET}\n")
            try:
                input()
            except KeyboardInterrupt:
                print(f"\n  {C.DIM}Goodbye.{C.RESET}\n")
                sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n  {C.DIM}Session ended. Goodbye.{C.RESET}\n")
        sys.exit(0)
