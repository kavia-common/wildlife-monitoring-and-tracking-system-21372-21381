# Database Layer (MongoDB)

This backend uses MongoDB (async) via Motor.

Key components:
- connection.py: Manages async client, database lifecycle, settings, and index creation.
- models.py: Pydantic models for domain entities (users, animals, devices, telemetry, geofences, alerts, sightings).
- __init__.py: Exposes get_database(), get_collection(), init_indexes(), close_database().
- sample_data.py: API utilities to seed and verify sample data across all collections.
- cli.py: CLI entrypoint to seed/verify without running the server.

Environment:
- Copy .env.example to .env and set MONGODB_URI and MONGODB_DB_NAME.

Startup:
- App connects and ensures indexes on FastAPI startup events.
- 2dsphere indexes are defined for location-aware collections (telemetry, geofences, sightings).

Seeding sample data:
- REST:
  - POST /sample/seed -> inserts one realistic record into: users, animals, devices, telemetry (3 points), geofences, alerts, sightings.
  - GET  /sample/verify -> counts docs per collection and fetches latest telemetry; returns ok=true on success.
- CLI:
  - python -m src.api.cli seed
  - python -m src.api.cli verify
  - python -m src.api.cli seed-verify

Usage:
- from src.db import get_collection
- telemetry = get_collection("telemetry")
- await telemetry.insert_one({...})

No migrations are used; MongoDB collections are provisioned lazily via index creation.
