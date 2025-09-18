"""
Database package initializer.

This module exposes the key database interfaces:
- get_database: returns the AsyncIOMotorDatabase instance
- get_collection: returns a specific collection from the configured database
- init_indexes: ensures indexes are created at startup
"""

from .connection import get_database, get_collection, close_database, init_indexes

__all__ = ["get_database", "get_collection", "close_database", "init_indexes"]
