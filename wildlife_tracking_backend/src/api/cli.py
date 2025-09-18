"""
CLI utilities for seeding and verifying MongoDB sample data.

Usage:
    python -m src.api.cli seed        # Seed data
    python -m src.api.cli verify      # Verify data
    python -m src.api.cli seed-verify # Seed and then verify

Note: Requires MONGODB_URI and MONGODB_DB_NAME environment variables set in .env.
"""

import asyncio
import sys
import json
import logging

from src.db.connection import ensure_database, init_indexes, close_database
from src.api.sample_data import seed_sample_data, verify_sample_data, seed_and_verify

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cli")


async def _run(cmd: str):
    await ensure_database()
    await init_indexes()
    try:
        if cmd == "seed":
            res = await seed_sample_data()
            print(json.dumps(res.model_dump(), default=str, indent=2))
        elif cmd == "verify":
            res = await verify_sample_data()
            print(json.dumps(res.model_dump(), default=str, indent=2))
        elif cmd == "seed-verify":
            res = await seed_and_verify()
            print(json.dumps(res, default=str, indent=2))
        else:
            print("Unknown command. Use one of: seed | verify | seed-verify", file=sys.stderr)
            sys.exit(2)
    finally:
        await close_database()


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.api.cli [seed|verify|seed-verify]", file=sys.stderr)
        sys.exit(2)
    cmd = sys.argv[1]
    asyncio.run(_run(cmd))


if __name__ == "__main__":
    main()
