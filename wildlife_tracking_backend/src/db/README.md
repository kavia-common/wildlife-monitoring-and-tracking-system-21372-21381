# Database Layer (MongoDB)

This backend uses MongoDB (async) via Motor.

Key components:
- connection.py: Manages async client, database lifecycle, settings, and index creation.
- models.py: Pydantic models for domain entities (users, animals, devices, telemetry, geofences, alerts, sightings).
- __init__.py: Exposes get_database(), get_collection(), init_indexes(), close_database().

Environment:
- Copy .env.example to .env and set MONGODB_URI and MONGODB_DB_NAME.

Startup:
- App connects and ensures indexes on FastAPI startup events.
- 2dsphere indexes are defined for location-aware collections (telemetry, geofences, sightings).

Usage:
- from src.db import get_collection
- telemetry = get_collection("telemetry")
- await telemetry.insert_one({...})

No migrations are used; MongoDB collections are provisioned lazily via index creation.
