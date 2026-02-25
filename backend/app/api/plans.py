import httpx
from fastapi import APIRouter, Depends, HTTPException

from ..api.profile import get_profile
from ..core.auth import get_current_user_id
from ..core.config import SERVICE_HEADERS, SUPABASE_URL
from ..models.schemas import GeneratePlanRequest
from ..optimiser.engine import TrainingPlanOptimiser, InfeasiblePlanError

router = APIRouter(prefix="/api/plans")

GOAL_MAP = {
    "Hypertrophy": "hypertrophy",
    "Strength": "strength",
    "Fat loss": "fat_loss",
    "General fitness": "general_fitness",
}


async def _insert_plan(user_id: str, request_json: dict) -> dict:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{SUPABASE_URL}/rest/v1/plans",
            headers=SERVICE_HEADERS,
            json={"user_id": user_id, "status": "running", "request_json": request_json},
        )
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Failed to create plan row: {resp.text}")
    return resp.json()[0]


async def _update_plan(plan_id: str, data: dict) -> None:
    async with httpx.AsyncClient() as client:
        await client.patch(
            f"{SUPABASE_URL}/rest/v1/plans",
            params={"id": f"eq.{plan_id}"},
            headers=SERVICE_HEADERS,
            json=data,
        )


def _build_optimiser_input(profile: dict) -> dict:
    """Map profile columns to the shape GeneratePlanRequest expects."""
    goal_raw = profile.get("training_goal") or ""
    goal_key = GOAL_MAP.get(goal_raw, goal_raw.lower().replace(" ", "_"))

    days = profile.get("available_days") or []
    equipment = profile.get("equipment") or []

    squat = profile.get("squat_1rm")
    bench = profile.get("bench_1rm")
    deadlift = profile.get("deadlift_1rm")
    ohp = profile.get("ohp_1rm")
    if not all(v is not None and v > 0 for v in (squat, bench, deadlift, ohp)):
        raise HTTPException(
            status_code=400,
            detail="All four one-rep maxes (Squat, Bench, Deadlift, OHP) are required for plan generation.",
        )

    return {
        "training_goal": goal_key,
        "available_days": [d.lower() for d in days],
        "session_duration_minutes": profile.get("session_duration_min") or 60,
        "equipment": [e.lower() for e in equipment],
        "one_rep_maxes": {
            "squat_1rm": squat,
            "bench_1rm": bench,
            "deadlift_1rm": deadlift,
            "ohp_1rm": ohp,
        },
        "required_primary_lifts": profile.get("required_primary_lifts") or [],
        "excluded_exercises": profile.get("excluded_exercises") or [],
        "include_cardio": profile.get("include_cardio", False),
    }


@router.get("/latest")
async def get_latest_plan(user_id: str = Depends(get_current_user_id)):
    select = "id,status,request_json,response_json,error_message,created_at"
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{SUPABASE_URL}/rest/v1/plans",
            params={
                "user_id": f"eq.{user_id}",
                "select": select,
                "order": "created_at.desc",
                "limit": "1",
            },
            headers=SERVICE_HEADERS,
        )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch plans: {resp.text}")
    rows = resp.json()
    if not rows:
        raise HTTPException(status_code=404, detail="No plans found. Generate your first plan to get started.")
    return rows[0]


@router.post("/generate")
async def generate_plan(user_id: str = Depends(get_current_user_id)):
    profile = await get_profile(user_id)

    if not profile.get("onboarding_completed"):
        raise HTTPException(status_code=400, detail="Onboarding not completed.")

    request_snapshot = _build_optimiser_input(profile)

    plan_row = await _insert_plan(user_id, request_snapshot)
    plan_id = plan_row["id"]

    try:
        optimiser_request = GeneratePlanRequest(**request_snapshot)
        result = TrainingPlanOptimiser(optimiser_request).solve()
        result_json = result.model_dump(mode="json")

        await _update_plan(plan_id, {"status": "success", "response_json": result_json})
        return {"plan_id": plan_id, "status": "success", "response_json": result_json}

    except InfeasiblePlanError as e:
        error_msg = str(e)
        await _update_plan(plan_id, {"status": "error", "error_message": error_msg})
        return {"plan_id": plan_id, "status": "error", "error_message": error_msg}

    except Exception:
        await _update_plan(plan_id, {"status": "error", "error_message": "internal error"})
        return {"plan_id": plan_id, "status": "error", "error_message": "internal error"}
