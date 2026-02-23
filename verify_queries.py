import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db.database import initialize_db
from modules.reports import REPORT_MENU


def print_divider(title: str):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)


def print_rows(rows):
    if not rows:
        print("  (no results)")
        return
    # Print column headers
    keys = rows[0].keys()
    col_widths = {k: max(len(str(k)), max(len(str(row[k] or '')) for row in rows))
                  for k in keys}
    header = "  " + " | ".join(str(k).ljust(col_widths[k]) for k in keys)
    sep    = "  " + "-+-".join("-" * col_widths[k] for k in keys)
    print(header)
    print(sep)
    for row in rows:
        print("  " + " | ".join(str(row[k] or '').ljust(col_widths[k]) for k in keys))
    print(f"\n  [{len(rows)} row(s) returned]")


if __name__ == '__main__':
    print("\n[ERP SIMULATION] Initializing database...")
    initialize_db(seed=True)

    print("\n[ERP SIMULATION] Running all 10 business queries...\n")

    for i, (label, fn) in enumerate(REPORT_MENU, 1):
        print_divider(f"Query {i:02d}: {label}")
        rows = fn()
        print_rows(rows)

    print("\n" + "=" * 65)
    print("  All 10 queries executed successfully.")
    print("=" * 65 + "\n")
