# Login, session management, and permission enforcement.
# TODO: Possible refactor on CRM development for stricter enforcement?

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from db.database import get_connection


# ── Permission Levels ────────────────────────────────
PERMISSION_LABELS = {
    1: "Viewer",
    2: "Sales Rep",
    3: "Supervisor",
    4: "Manager",
    5: "Administrator",
}

# ─ ANSI Colors ─
class C:
    BOLD    = "\033[1m"
    GREEN   = "\033[92m"
    RED     = "\033[91m"
    YELLOW  = "\033[93m"
    CYAN    = "\033[96m"
    BLUE    = "\033[94m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"

    @classmethod
    def disable(cls):
        for attr in ["BOLD","GREEN","RED","YELLOW","CYAN","BLUE","DIM","RESET"]:
            setattr(cls, attr, "")


# ── Menu utils ───────────────────────────────────────────────────

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def divider(char="─", width=62):
    print(C.DIM + char * width + C.RESET)


def print_banner():
    clear()
    print(C.BLUE + C.BOLD)
    print("  ╔══════════════════════════════════════════════════════╗")
    print("  ║          ERP SIMULATION SYSTEM  v1.0                 ║")
    print("  ╚══════════════════════════════════════════════════════╝")
    print(C.RESET)


def print_header(session):
    """Prints the top-of-screen session bar for every menu."""
    divider("═")
    name  = session["name"]
    role  = session["role"]
    level = session["level"]
    dept  = session["department"]
    print(
        f"  {C.BOLD}{C.CYAN}{name}{C.RESET}"
        f"  {C.DIM}|{C.RESET}"
        f"  {C.YELLOW}{role}{C.RESET}"
        f"  {C.DIM}|{C.RESET}"
        f"  Level {level}"
        f"  {C.DIM}|{C.RESET}"
        f"  {dept}"
    )
    divider("═")
    print()


def ok(msg):
    print(f"\n  {C.GREEN}{C.BOLD}[OK]{C.RESET}    {msg}")


def err(msg):
    print(f"\n  {C.RED}{C.BOLD}[ERROR]{C.RESET}  {msg}")


def warn(msg):
    print(f"\n  {C.YELLOW}{C.BOLD}[WARN]{C.RESET}   {msg}")


def pause():
    print()
    input("  Press Enter to continue...")


def login() -> dict | None:
    # Prompt for an employee ID and return a session dict if found and active.
    print_banner()
    divider()
    print(f"  {C.BOLD}Login{C.RESET}  —  Enter your Employee ID to continue.")
    print(f"  {C.DIM}(Type 'exit' to quit){C.RESET}")
    divider()
    print()

    while True:
        raw = input("  Employee ID: ").strip()

        if raw.lower() == 'exit':
            print(f"\n  {C.DIM}Goodbye.{C.RESET}\n")
            sys.exit(0)

        if not raw.isdigit():
            err("Employee ID must be a number.")
            continue

        emp_id = int(raw)
        conn = get_connection()

        #TODO: Refactor from here
        row = conn.execute("""
            SELECT
                e.id,
                e.first_name || ' ' || e.last_name  AS name,
                e.is_active,
                r.name                              AS role,
                r.permission_level                  AS level,
                d.name                              AS department
            FROM employees e
            JOIN roles r       ON e.role_id       = r.id
            JOIN departments d ON e.department_id = d.id
            WHERE e.id = ?
        """, (emp_id,)).fetchone()
        conn.close()

        #-----------------------------------------------

        if not row:
            err(f"No employee found with ID {emp_id}. Try again.")
            continue

        if not row["is_active"]:
            err(
                f"Account for '{row['name']}' is inactive. "
                "Contact your administrator."
            )
            continue

        session = {
            "id":         row["id"],
            "name":       row["name"],
            "role":       row["role"],
            "level":      row["level"],
            "department": row["department"],
        }

        ok(f"Welcome, {session['name']}!  "
           f"Logged in as {C.YELLOW}{session['role']}{C.RESET}"
           f"  (Permission Level {session['level']})")
        pause()
        return session


# ── Permission Enforcement ────────────────────────────────────

def require_permission(session: dict, min_level: int, action: str = "this action") -> bool:
    # Returns True if the session meets min_level.
    if session["level"] >= min_level:
        return True

    needed_role = PERMISSION_LABELS.get(min_level, f"Level {min_level}")
    err(
        f"Access denied. '{action}' requires {C.YELLOW}{needed_role}{C.RESET}"
        f" (Level {min_level}+).\n"
        f"  Your current role: {C.YELLOW}{session['role']}{C.RESET}"
        f" (Level {session['level']})."
    )
    return False


# ── Input utils for all components in modules/ ───────────────────

def get_int_input(prompt: str, min_val: int = None, max_val: int = None) -> int | None:
    while True:
        raw = input(f"  {prompt}").strip()
        if raw == '' or raw == '0':
            return None
        if not raw.lstrip('-').isdigit():
            err("Please enter a valid number.")
            continue
        val = int(raw)
        if min_val is not None and val < min_val:
            err(f"Value must be at least {min_val}.")
            continue
        if max_val is not None and val > max_val:
            err(f"Value must be no more than {max_val}.")
            continue
        return val


def get_str_input(prompt: str, max_len: int = 200, allow_blank: bool = False) -> str | None:
    while True:
        raw = input(f"  {prompt}").strip()
        if raw == '0':
            return None
        if not allow_blank and not raw:
            err("This field cannot be blank.")
            continue
        if len(raw) > max_len:
            err(f"Input too long (max {max_len} characters).")
            continue
        return raw


def get_choice(prompt: str, valid: list) -> str | None:
    while True:
        raw = input(f"  {prompt}").strip().lower()
        if raw == '0':
            return None
        if raw in [str(v).lower() for v in valid]:
            return raw
        err(f"Invalid choice. Options: {', '.join(str(v) for v in valid)}")
