import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.auth import (
    require_permission, print_header, warn, pause, divider, get_choice, C
)
from modules.reports import REPORT_MENU

FINANCIAL_REPORT_INDEXES = {0, 1, 8, 9}  # Monthly Revenue, Dept Revenue, Dept Payroll, Access Audit

def _print_report(label: str, rows: list):
    print(f"\n  {C.BOLD}{C.CYAN}{label}{C.RESET}\n")

    if not rows:
        warn("No data returned for this report.")
        return

    keys = list(rows[0].keys())

    # Calculate column widths from headers and data
    widths = {k: len(str(k)) for k in keys}
    for row in rows:
        for k in keys:
            widths[k] = max(widths[k], len(str(row[k] or "—")))

    # Cap column at 36 chars
    for k in widths:
        widths[k] = min(widths[k], 36)

    def fmt(val, width):
        return str(val or "—")[:width].ljust(width)

    # Header row
    divider("─", sum(widths.values()) + len(keys) * 3 + 2)
    print(C.BOLD + "  " + "   ".join(str(k).upper()[:widths[k]].ljust(widths[k]) for k in keys) + C.RESET)
    divider("─", sum(widths.values()) + len(keys) * 3 + 2)

    for row in rows:
        parts = []
        for k in keys:
            val = row[k]
            raw = str(val or "—")[:widths[k]]
            try:
                float(str(val).replace(",", "").replace("$", ""))
                parts.append(f"{C.CYAN}{raw.ljust(widths[k])}{C.RESET}")
            except (ValueError, TypeError):
                parts.append(raw.ljust(widths[k]))
        print("  " + "   ".join(parts))

    divider("─", sum(widths.values()) + len(keys) * 3 + 2)
    print(f"  {C.DIM}{len(rows)} row(s) returned.{C.RESET}\n")


def _run_report(session: dict, index: int):
    label, fn = REPORT_MENU[index]

    # Determine required permission level
    required = 4 if index in FINANCIAL_REPORT_INDEXES else 3

    if not require_permission(session, required, label):
        pause()
        return

    print_header(session)
    rows = fn()
    _print_report(label, rows)
    pause()


def reports_menu(session: dict):
    if not require_permission(session, 3, "Reports"):
        pause()
        return

    while True:
        print_header(session)
        print(f"  {C.BOLD}Business Reports{C.RESET}")
        print(f"  {C.DIM}Your access level: {session['role']} (Level {session['level']}){C.RESET}\n")
        divider()

        for i, (label, _) in enumerate(REPORT_MENU, 1):
            idx = i - 1
            is_financial = idx in FINANCIAL_REPORT_INDEXES
            locked = is_financial and session["level"] < 4

            tag = f"{C.YELLOW} [Level 4+]{C.RESET}" if locked else ""
            dim = C.DIM if locked else ""
            rst = C.RESET if locked else ""

            print(f"  {dim}[{i:>2}] {label}{rst}{tag}")

        print()
        print(f"  {C.DIM}[ 0] Back to Main Menu{C.RESET}")
        divider()

        valid = ["0"]
        for i, (_, _) in enumerate(REPORT_MENU, 1):
            idx = i - 1
            is_financial = idx in FINANCIAL_REPORT_INDEXES
            if not (is_financial and session["level"] < 4):
                valid.append(str(i))

        choice = get_choice("Select report: ", valid)
        if not choice or choice == "0":
            return

        _run_report(session, int(choice) - 1)
