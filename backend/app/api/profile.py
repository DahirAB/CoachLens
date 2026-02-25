import httpx
from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import get_current_user_id
from ..core.config import SERVICE_HEADERS, SUPABASE_URL
from ..models.schemas import OnboardingRequest
from ..optimiser.data import EXERCISES

router = APIRouter(prefix="/api/profile")

PRIMARY_LIFT_LABELS = {
    "squat_1rm": "Squat",
    "bench_1rm": "Bench Press",
    "deadlift_1rm": "Deadlift",
    "ohp_1rm": "Overhead Press",
}


@router.get("")
async def get_profile(
    user_id: str = Depends(get_current_user_id),
):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/profiles",
            params={"id": f"eq.{user_id}", "select": "*"},
            headers={
                **SERVICE_HEADERS,
                "Accept": "application/json",
            },
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Profile fetch failed: {resp.text}")
    rows = resp.json()
    if not rows:
        raise HTTPException(status_code=404, detail="Profile not found")
    return rows[0]


@router.get("/exercise-catalog")
async def get_exercise_catalog():
    seen: dict[str, dict] = {}
    for ex in EXERCISES:
        is_cardio = ex.tier.value == "cardio" or ex.pattern.value == "cardio"
        if ex.name in seen:
            seen[ex.name]["equipment"].add(ex.equipment.value)
        else:
            seen[ex.name] = {
                "id": ex.name,
                "label": ex.name,
                "equipment": {ex.equipment.value},
                "is_cardio": is_cardio,
            }

    exercises = [
        {**entry, "equipment": sorted(entry["equipment"])}
        for entry in seen.values()
    ]

    primary_lifts = [
        {"id": k, "label": v} for k, v in PRIMARY_LIFT_LABELS.items()
    ]

    return {"exercises": exercises, "primary_lifts": primary_lifts}


@router.patch("/onboarding")
async def update_onboarding(
    body: OnboardingRequest,
    user_id: str = Depends(get_current_user_id),
):
    required_lifts = body.required_primary_lifts or []
    excluded = body.excluded_exercises or []

    if len(required_lifts) > 3:
        raise HTTPException(422, detail="You may require at most 3 primary lifts.")
    if len(excluded) > 10:
        raise HTTPException(422, detail="You may exclude at most 10 exercises.")

    equipment_lower = [e.lower() for e in body.equipment]
    equip = set(equipment_lower)
    excluded_set = set(excluded)
    for lift_key in required_lifts:
        candidates = [
            ex for ex in EXERCISES
            if ex.primary_1rm_link == lift_key
            and ex.equipment.value in equip
            and ex.name not in excluded_set
        ]
        if not candidates:
            raise HTTPException(
                422,
                detail=f"No feasible exercise for required lift {lift_key} with your equipment and exclusions.",
            )

    update_data: dict = {
        "training_goal": body.training_goal.lower().replace(" ", "_"),
        "available_days": [d.lower() for d in body.available_days],
        "session_duration_min": body.session_duration_min,
        "equipment": equipment_lower,
        "include_cardio": body.include_cardio,
        "squat_1rm": body.squat_1rm,
        "bench_1rm": body.bench_1rm,
        "deadlift_1rm": body.deadlift_1rm,
        "ohp_1rm": body.ohp_1rm,
        "required_primary_lifts": required_lifts,
        "excluded_exercises": excluded,
        "onboarding_completed": True,
    }

    if body.first_name is not None:
        update_data["first_name"] = body.first_name

    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"{SUPABASE_URL}/rest/v1/profiles",
            params={"id": f"eq.{user_id}"},
            headers=SERVICE_HEADERS,
            json=update_data,
        )

    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Profile update failed: {resp.text}")

    rows = resp.json()
    if not rows:
        raise HTTPException(
            status_code=500,
            detail="Profile row not found for user; check auth->profiles trigger.",
        )

    return rows[0]
