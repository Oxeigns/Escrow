import argparse
import asyncio
from database.mongo import db
from bot.blacklist import add_to_blacklist, remove_from_blacklist
from bot.escrow import list_escrows


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

    if args.cmd == "blacklist":
        await add_to_blacklist(args.telegram_id, args.reason, args.severity)
        print("OK: user blacklisted")
    elif args.cmd == "unblacklist":
        await remove_from_blacklist(args.telegram_id)
        print("OK: user unblacklisted")
    elif args.cmd == "escrows":
        rows = await list_escrows()
        for r in rows:
            print(r)
    else:
        parser.print_help()


if __name__ == "__main__":
    asyncio.run(main())
