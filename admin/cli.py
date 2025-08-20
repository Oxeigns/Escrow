import argparse
import asyncio
import sys
from pathlib import Path

"""Command line interface for admin tasks.

This script is intended to be executed directly via ``python admin/cli.py``.
When launched this way Python sets ``sys.path[0]`` to the script's directory
(``admin``) which means the project root is not on the import path.  As a
result absolute imports such as ``from bot.blacklist import ...`` would fail
with ``ModuleNotFoundError``.  To make the CLI runnable without requiring
``python -m`` we explicitly append the repository root to ``sys.path`` before
performing package imports.
"""

# Ensure project root is on ``sys.path`` for absolute imports
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

async def main():
    parser = argparse.ArgumentParser(description="Admin panel CLI")
    sub = parser.add_subparsers(dest="cmd")

    b = sub.add_parser("blacklist")
    b.add_argument("telegram_id", type=int)
    b.add_argument("--reason", default="violation")
    b.add_argument("--severity", type=int, default=1)

    ub = sub.add_parser("unblacklist")
    ub.add_argument("telegram_id", type=int)

    es = sub.add_parser("escrows")

    args = parser.parse_args()

    # Import heavy modules lazily so ``--help`` doesn't require optional deps
    if args.cmd == "blacklist":
        from bot.blacklist import add_to_blacklist

        await add_to_blacklist(args.telegram_id, args.reason, args.severity)
        print("OK: user blacklisted")
    elif args.cmd == "unblacklist":
        from bot.blacklist import remove_from_blacklist

        await remove_from_blacklist(args.telegram_id)
        print("OK: user unblacklisted")
    elif args.cmd == "escrows":
        from bot.escrow import list_escrows

        rows = await list_escrows()
        for r in rows:
            print(r)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
