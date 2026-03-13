#!/usr/bin/env python3
"""Usage budget monitor for test harness work.

Tracks estimated Claude Code session costs against a weekly budget so that
test harness work can be spread across multiple weeks without exceeding
usage limits.

The budget configuration lives in CLAUDE.md (not tracked):
    WEEKLY_BUDGET_USD=5.00
    BUDGET_LIMIT_PCT=20

Usage:
    python3 monitor.py status              # Show current week's usage vs budget
    python3 monitor.py log <cost> [desc]   # Log a session cost
    python3 monitor.py history             # Show all logged sessions
    python3 monitor.py reset               # Clear the ledger (fresh start)

Programmatic:
    from monitor import check_budget, log_session, get_status
    ok, info = check_budget()
    if not ok:
        print(f"Over budget: {info}")
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

HARNESS_DIR = Path(__file__).resolve().parent
LEDGER_FILE = HARNESS_DIR / "data" / "usage.json"
CLAUDE_MD = HARNESS_DIR / "CLAUDE.md"

# Defaults if not configured in CLAUDE.md
DEFAULT_WEEKLY_BUDGET_USD = 5.00
DEFAULT_BUDGET_LIMIT_PCT = 20


def _load_ledger():
    """Load the usage ledger."""
    if LEDGER_FILE.exists():
        try:
            return json.loads(LEDGER_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return {"sessions": []}
    return {"sessions": []}


def _save_ledger(data):
    """Save the usage ledger."""
    LEDGER_FILE.parent.mkdir(parents=True, exist_ok=True)
    LEDGER_FILE.write_text(json.dumps(data, indent=2) + "\n")


def _parse_claude_md_config():
    """Parse budget config from CLAUDE.md.

    Looks for lines like:
        WEEKLY_BUDGET_USD=5.00
        BUDGET_LIMIT_PCT=20
    """
    config = {
        "weekly_budget_usd": DEFAULT_WEEKLY_BUDGET_USD,
        "budget_limit_pct": DEFAULT_BUDGET_LIMIT_PCT,
    }

    if not CLAUDE_MD.exists():
        return config

    text = CLAUDE_MD.read_text()

    m = re.search(r'WEEKLY_BUDGET_USD\s*=\s*([\d.]+)', text)
    if m:
        config["weekly_budget_usd"] = float(m.group(1))

    m = re.search(r'BUDGET_LIMIT_PCT\s*=\s*(\d+)', text)
    if m:
        config["budget_limit_pct"] = int(m.group(1))

    return config


def _week_start():
    """Get the start of the current ISO week (Monday 00:00 UTC)."""
    now = datetime.now(timezone.utc)
    monday = now - timedelta(days=now.weekday())
    return monday.replace(hour=0, minute=0, second=0, microsecond=0)


def _this_week_sessions(ledger):
    """Filter sessions to the current week."""
    start = _week_start()
    sessions = []
    for s in ledger.get("sessions", []):
        try:
            ts = datetime.fromisoformat(s["timestamp"])
            if ts >= start:
                sessions.append(s)
        except (KeyError, ValueError):
            pass
    return sessions


def get_status():
    """Get current budget status.

    Returns dict with:
        weekly_budget_usd, budget_limit_pct, effective_budget,
        week_spent, remaining, pct_used, over_budget,
        session_count, week_start
    """
    config = _parse_claude_md_config()
    ledger = _load_ledger()
    week_sessions = _this_week_sessions(ledger)

    effective = config["weekly_budget_usd"] * config["budget_limit_pct"] / 100
    spent = sum(s.get("cost_usd", 0) for s in week_sessions)
    remaining = max(0, effective - spent)
    pct_used = (spent / effective * 100) if effective > 0 else 100

    return {
        "weekly_budget_usd": config["weekly_budget_usd"],
        "budget_limit_pct": config["budget_limit_pct"],
        "effective_budget": effective,
        "week_spent": spent,
        "remaining": remaining,
        "pct_used": pct_used,
        "over_budget": spent >= effective,
        "session_count": len(week_sessions),
        "week_start": _week_start().isoformat(),
    }


def check_budget():
    """Check if we're within budget.

    Returns (ok: bool, status: dict).
    """
    status = get_status()
    return not status["over_budget"], status


def log_session(cost_usd, description=""):
    """Log a session's cost to the ledger.

    Args:
        cost_usd: Estimated cost in USD (from Claude Code /cost command)
        description: What was done in this session
    """
    ledger = _load_ledger()
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cost_usd": round(float(cost_usd), 4),
    }
    if description:
        entry["description"] = description
    ledger["sessions"].append(entry)
    _save_ledger(ledger)
    return entry


def _format_status(status):
    """Format status for display."""
    lines = []
    lines.append(f"Week starting: {status['week_start'][:10]}")
    lines.append(f"Budget: ${status['weekly_budget_usd']:.2f}/week "
                 f"x {status['budget_limit_pct']}% "
                 f"= ${status['effective_budget']:.2f} for test harness")
    lines.append(f"Spent this week: ${status['week_spent']:.4f} "
                 f"({status['pct_used']:.1f}% of allocation)")
    lines.append(f"Remaining: ${status['remaining']:.4f}")
    lines.append(f"Sessions this week: {status['session_count']}")

    if status["over_budget"]:
        lines.append("\n** OVER BUDGET — defer remaining work to next week **")
    elif status["pct_used"] > 80:
        lines.append("\n** Approaching budget limit — wrap up soon **")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Usage budget monitor for test harness")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("status", help="Show current week's usage vs budget")

    log_p = sub.add_parser("log", help="Log a session cost")
    log_p.add_argument("cost", type=float, help="Cost in USD")
    log_p.add_argument("description", nargs="?", default="",
                       help="What was done")

    sub.add_parser("history", help="Show all logged sessions")
    sub.add_parser("reset", help="Clear the ledger")

    args = parser.parse_args()

    if not args.command:
        args.command = "status"

    if args.command == "status":
        status = get_status()
        print(_format_status(status))

    elif args.command == "log":
        entry = log_session(args.cost, args.description)
        print(f"Logged: ${entry['cost_usd']:.4f}"
              + (f" — {entry.get('description', '')}" if entry.get("description") else ""))
        print()
        status = get_status()
        print(_format_status(status))

    elif args.command == "history":
        ledger = _load_ledger()
        sessions = ledger.get("sessions", [])
        if not sessions:
            print("No sessions logged.")
            return

        print(f"{'Date':<22s} {'Cost':>8s}  Description")
        print("-" * 60)
        total = 0
        for s in sessions:
            ts = s.get("timestamp", "?")[:19]
            cost = s.get("cost_usd", 0)
            desc = s.get("description", "")
            print(f"{ts:<22s} ${cost:>7.4f}  {desc}")
            total += cost
        print("-" * 60)
        print(f"{'Total':<22s} ${total:>7.4f}")

    elif args.command == "reset":
        _save_ledger({"sessions": []})
        print("Ledger cleared.")


if __name__ == "__main__":
    main()
