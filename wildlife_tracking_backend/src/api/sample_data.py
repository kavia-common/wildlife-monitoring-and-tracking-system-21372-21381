import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.db.connection import get_collection, ensure_database
from src.db.models import User, Animal, Device, TelemetryPoint, Geofence, Alert, Sighting

logger = logging.getLogger("sample_data")
logger.setLevel(logging.INFO)

router = APIRouter(
    prefix="/sample",
    tags=["sample-data"],
)

# Utility helpers


def _geo_point(lon: float, lat: float) -> dict:
    return {"type": "Point", "coordinates": [lon, lat]}


def _geo_polygon(coords: List[List[List[float]]]) -> dict:
    return {"type": "Polygon", "coordinates": coords}


async def _insert_one(collection_name: str, doc: Dict[str, Any]) -> str:
    coll = get_collection(collection_name)
    res = await coll.insert_one(doc)
    return str(res.inserted_id)


async def _upsert_one(collection_name: str, query: Dict[str, Any], doc: Dict[str, Any]) -> str:
    """Upsert and return id."""
    coll = get_collection(collection_name)
    res = await coll.update_one(query, {"$setOnInsert": doc}, upsert=True)
    if res.upserted_id:
        return str(res.upserted_id)
    # when not inserted, fetch existing id
    existing = await coll.find_one(query, {"_id": 1})
    return str(existing["_id"]) if existing else ""


class SeedResult(BaseModel):
    users_id: str
    animals_id: str
    devices_id: str
    telemetry_ids: List[str]
    geofence_id: str
    alert_id: str
    sighting_id: str


# PUBLIC_INTERFACE
@router.post(
    "/seed",
    summary="Seed sample/mock data",
    description="Insert realistic sample documents into MongoDB across core collections: users, animals, devices, telemetry, geofences, alerts, sightings.",
    response_model=SeedResult,
    responses={
        200: {"description": "Seed data created successfully"},
        500: {"description": "Error while inserting seed data"},
    },
)
async def seed_sample_data() -> SeedResult:
    """
    PUBLIC_INTERFACE
    Seeds the database with one realistic record in all core collections.

    Returns:
    - users_id, animals_id, devices_id, geofence_id, alert_id, sighting_id: inserted document IDs
    - telemetry_ids: list of inserted telemetry point IDs
    """
    await ensure_database()

    # 1. User
    user = User(
        email="researcher@example.org",
        name="Dr. Asha Rao",
        role="researcher",
    ).model_dump(exclude_none=True)
    user_id = await _upsert_one("users", {"email": user["email"]}, user)
    logger.info("Seeded user id=%s", user_id)

    # 2. Animal
    animal = Animal(
        species="Sloth Bear",
        tag_id="SB-001",
        sex="female",
        age_years=7.5,
        name="Tara",
    ).model_dump(exclude_none=True)
    animal_id = await _upsert_one("animals", {"tag_id": animal["tag_id"]}, animal)
    logger.info("Seeded animal id=%s", animal_id)

    # 3. Device
    device = Device(
        device_id="DEV-ALPHA-001",
        animal_id=animal_id,
        status="active",
        battery_level=88.5,
        last_seen_at=datetime.utcnow(),
    ).model_dump(exclude_none=True)
    device_id = await _upsert_one("devices", {"device_id": device["device_id"]}, device)
    logger.info("Seeded device id=%s", device_id)

    # 4. Geofence
    # Simple square polygon near a coordinate (e.g., Bandipur Tiger Reserve area approx)
    geofence_poly = _geo_polygon(
        [
            [
                [76.62, 11.64],
                [76.72, 11.64],
                [76.72, 11.72],
                [76.62, 11.72],
                [76.62, 11.64],
            ]
        ]
    )
    geofence = Geofence(
        name="Bandipur Zone A",
        description="Core monitoring area for sloth bears.",
        active=True,
        geometry=geofence_poly,
        created_by=user_id,
    ).model_dump(exclude_none=True)
    geofence_id = await _upsert_one("geofences", {"name": geofence["name"]}, geofence)
    logger.info("Seeded geofence id=%s", geofence_id)

    # 5. Telemetry - create a small route of 3 points within/around the geofence
    now = datetime.utcnow()
    telemetry_points = [
        TelemetryPoint(
            animal_id=animal_id,
            device_id=device_id,
            timestamp=now - timedelta(minutes=10),
            location=_geo_point(76.65, 11.66),
            speed_kmh=3.1,
            heart_rate_bpm=55.0,
            temperature_c=36.8,
        ),
        TelemetryPoint(
            animal_id=animal_id,
            device_id=device_id,
            timestamp=now - timedelta(minutes=5),
            location=_geo_point(76.67, 11.68),
            speed_kmh=4.2,
            heart_rate_bpm=58.0,
            temperature_c=36.9,
        ),
        TelemetryPoint(
            animal_id=animal_id,
            device_id=device_id,
            timestamp=now - timedelta(minutes=1),
            location=_geo_point(76.69, 11.70),
            speed_kmh=2.5,
            heart_rate_bpm=54.0,
            temperature_c=36.7,
        ),
    ]
    telemetry_ids: List[str] = []
    for tp in telemetry_points:
        tp_id = await _insert_one("telemetry", tp.model_dump(exclude_none=True))
        telemetry_ids.append(tp_id)
    logger.info("Seeded telemetry ids=%s", telemetry_ids)

    # 6. Alert
    alert = Alert(
        animal_id=animal_id,
        type="geofence_breach",
        message="Animal Tara crossed the northern boundary of Bandipur Zone A.",
        status="open",
        metadata={"geofence_id": geofence_id, "severity": "medium"},
    ).model_dump(exclude_none=True)
    alert_id = await _insert_one("alerts", alert)
    logger.info("Seeded alert id=%s", alert_id)

    # 7. Sighting
    sighting = Sighting(
        species="Sloth Bear",
        reporter_id=user_id,
        timestamp=now - timedelta(hours=1),
        location=_geo_point(76.68, 11.69),
        notes="Observed foraging near termite mound. No cubs observed.",
        media_urls=["https://example.org/media/sighting1.jpg"],
        confidence=0.9,
    ).model_dump(exclude_none=True)
    sighting_id = await _insert_one("sightings", sighting)
    logger.info("Seeded sighting id=%s", sighting_id)

    return SeedResult(
        users_id=user_id,
        animals_id=animal_id,
        devices_id=device_id,
        telemetry_ids=telemetry_ids,
        geofence_id=geofence_id,
        alert_id=alert_id,
        sighting_id=sighting_id,
    )


class VerifyResult(BaseModel):
    ok: bool = Field(..., description="Overall verification status")
    counts: Dict[str, int] = Field(..., description="Document counts for each collection")
    latest_telemetry: Optional[Dict[str, Any]] = Field(default=None, description="Most recent telemetry point for seeded animal")
    errors: Optional[List[str]] = Field(default=None, description="Any error messages encountered")


# PUBLIC_INTERFACE
@router.get(
    "/verify",
    summary="Verify sample data",
    description="Verifies seeded data by counting documents in each collection and fetching latest telemetry for the seeded animal.",
    response_model=VerifyResult,
)
async def verify_sample_data() -> VerifyResult:
    """
    PUBLIC_INTERFACE
    Verifies that sample data exists and is queryable.

    Returns:
    - ok: whether verification succeeded
    - counts: per-collection counts of documents
    - latest_telemetry: last telemetry point for the sample animal (if available)
    - errors: any errors encountered during verification
    """
    await ensure_database()
    errors: List[str] = []

    collections = ["users", "animals", "devices", "telemetry", "geofences", "alerts", "sightings"]
    counts: Dict[str, int] = {}
    try:
        for name in collections:
            coll = get_collection(name)
            counts[name] = await coll.count_documents({})
            logger.info("Count %s = %d", name, counts[name])
    except Exception as e:
        logger.exception("Error counting documents: %s", e)
        errors.append(f"count_error: {e!r}")

    latest_telemetry: Optional[Dict[str, Any]] = None
    try:
        # Find the latest telemetry overall, or you can filter by the animal created by seed
        coll = get_collection("telemetry")
        latest_telemetry = await coll.find_one({}, sort=[("timestamp", -1)])
        if latest_telemetry:
            # Convert ObjectId to str for safe JSON
            latest_telemetry["_id"] = str(latest_telemetry["_id"])
        logger.info("Latest telemetry: %s", latest_telemetry)
    except Exception as e:
        logger.exception("Error fetching latest telemetry: %s", e)
        errors.append(f"telemetry_fetch_error: {e!r}")

    ok = all(counts.get(c, 0) >= 1 for c in collections) and latest_telemetry is not None and len(errors) == 0
    return VerifyResult(ok=ok, counts=counts, latest_telemetry=latest_telemetry, errors=errors or None)


# PUBLIC_INTERFACE
async def seed_and_verify() -> Dict[str, Any]:
    """
    PUBLIC_INTERFACE
    Seed the database with sample data and perform verification in one async call.

    Returns a dict with the seed result and verify result for CLI use.
    """
    seed = await seed_sample_data()
    verify = await verify_sample_data()
    return {"seed": seed.model_dump(), "verify": verify.model_dump()}
