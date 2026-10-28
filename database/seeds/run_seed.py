"""
Runner script for seeding data into VirtuFit AI database.
Usage:
    python -m database.seeds.run_seed
or
    python -m backend.shared.database.seed
"""
import asyncio
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.shared.database.seed import run_seed

if __name__ == "__main__":
    asyncio.run(run_seed())
