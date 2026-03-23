from fastapi import APIRouter, Depends, HTTPException

from ..api.profile import get_profile
from ..core.auth import get_current_user_id
from ..core.config import SERVICE_HEADERS, SUPABASE_URL
from ..core.crypto import decrypt_json_payload, encrypt_json_payload
from ..core.http import get_http_client
from ..models.schemas import GeneratePlanRequest
from ..optimiser.data import EXERCISES
from ..optimiser.engine import TrainingPlanOptimiser, InfeasiblePlanError

router = APIRouter(prefix="/api/plans")

EXERCISE_1RM_MAP = {}
for _ex in EXERCISES:
    if _ex.primary_1rm_link:
        EXERCISE_1RM_MAP[_ex.name] = _ex.primary_1rm_link

_1RM_KEYS = ["squat_1rm", "bench_1rm", "deadlift_1rm", "ohp_1rm"]

GOAL_MAP = {
    "Hypertrophy": "hypertrophy",
    "Strength": "strength",
    "Fat loss": "fat_loss",
    "General fitness": "general_fitness",
}


async def _insert_plan(user_id: str, request_json: dict, parent_plan_id: str = None, week_number: int = 1) -> dict:
    client = get_http_client()
    payload = {
        "user_id": user_id,
        "status": "running",
        "request_json": encrypt_json_payload(request_json, aad_context=user_id),
        "week_number": week_number
    }
    if parent_plan_id:
        payload["parent_plan_id"] = parent_plan_id
    resp = await client.post(f"{SUPABASE_URL}/rest/v1/plans", headers=SERVICE_HEADERS, json=payload)
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Failed to create plan row: {resp.text}")
    return resp.json()[0]


async def _update_plan(plan_id: str, data: dict) -> None:
    write_data = dict(data)
    if "request_json" in write_data:
        write_data["request_json"] = encrypt_json_payload(
            write_data.get("request_json"),
            aad_context=write_data.get("user_id"),
        )
    if "response_json" in write_data:
        write_data["response_json"] = encrypt_json_payload(
            write_data.get("response_json"),
            aad_context=write_data.get("user_id"),
        )

    client = get_http_client()
    await client.patch(
        f"{SUPABASE_URL}/rest/v1/plans",
        params={"id": f"eq.{plan_id}"},
        headers=SERVICE_HEADERS,
        json=write_data,
    )


async def _get_plan_for_user(plan_id: str, user_id: str) -> dict:
    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plans",
        params={
            "id": f"eq.{plan_id}",
            "user_id": f"eq.{user_id}",
            "select": "id,user_id,status,created_at",
            "limit": "1",
        },
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch plan: {resp.text}")
    rows = resp.json()
    if not rows:
        raise HTTPException(status_code=404, detail="Plan not found")
    return rows[0]


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
    select = "id,status,request_json,response_json,error_message,created_at,week_number"
    client = get_http_client()
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
    row = rows[0]
    try:
        row["request_json"] = decrypt_json_payload(row.get("request_json"), aad_context=user_id)
        row["response_json"] = decrypt_json_payload(row.get("response_json"), aad_context=user_id)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Failed to decrypt plan data: {e}")
    return row


@router.post("/generate")
async def generate_plan(user_id: str = Depends(get_current_user_id)):
    profile = await get_profile(user_id)

    if not profile.get("onboarding_completed"):
        raise HTTPException(status_code=400, detail="Onboarding not completed.")

    request_snapshot = _build_optimiser_input(profile)

    plan_row = await _insert_plan(user_id, request_snapshot, parent_plan_id=None, week_number=1)
    plan_id = plan_row["id"]

    try:
        optimiser_request = GeneratePlanRequest(**request_snapshot)
        result = TrainingPlanOptimiser(optimiser_request).solve()
        result_json = result.model_dump(mode="json")

        await _update_plan(
            plan_id,
            {"status": "success", "response_json": result_json, "user_id": user_id},
        )
        return {"plan_id": plan_id, "status": "success", "response_json": result_json}

    except InfeasiblePlanError as e:
        error_msg = str(e)
        await _update_plan(plan_id, {"status": "error", "error_message": error_msg})
        return {"plan_id": plan_id, "status": "error", "error_message": error_msg}

    except Exception:
        await _update_plan(plan_id, {"status": "error", "error_message": "internal error"})
        return {"plan_id": plan_id, "status": "error", "error_message": "internal error"}


@router.delete("/{plan_id}")
async def delete_plan(
    plan_id: str,
    user_id: str = Depends(get_current_user_id),
):
    # Ownership check 
    await _get_plan_for_user(plan_id, user_id)

    client = get_http_client()
    resp = await client.delete(
        f"{SUPABASE_URL}/rest/v1/plans",
        params={"id": f"eq.{plan_id}", "user_id": f"eq.{user_id}"},
        headers=SERVICE_HEADERS,
    )
    if resp.status_code not in (200, 204):
        raise HTTPException(status_code=502, detail=f"Failed to delete plan: {resp.text}")

    return {"deleted": True, "plan_id": plan_id}


async def _get_full_plan(plan_id: str, user_id: str) -> dict:
    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plans",
        params={
            "id": f"eq.{plan_id}",
            "user_id": f"eq.{user_id}",
            "select": "id,user_id,status,request_json,response_json,week_number,created_at",
            "limit": "1",
        },
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch plan: {resp.text}")
    rows = resp.json()
    if not rows:
        raise HTTPException(status_code=404, detail="Plan not found")
    plan = rows[0]
    plan["request_json"] = decrypt_json_payload(plan.get("request_json"), aad_context=user_id)
    plan["response_json"] = decrypt_json_payload(plan.get("response_json"), aad_context=user_id)
    return plan


async def _get_tracking_rows(plan_id: str, user_id: str) -> list[dict]:
    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plan_tracking_daily",
        params={
            "plan_id": f"eq.{plan_id}",
            "user_id": f"eq.{user_id}",
            "select": "logged_date,day,entries_json",
            "order": "logged_date.asc",
        },
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch tracking: {resp.text}")
    return resp.json()


@router.get("/{plan_id}/progress/status")
async def get_progress_status(
    plan_id: str,
    user_id: str = Depends(get_current_user_id),
):
    plan = await _get_full_plan(plan_id, user_id)
    week_plan = plan["response_json"]["week_plan"]
    days_total = len(week_plan)
    tracking_rows = await _get_tracking_rows(plan_id, user_id)
    days_logged = len(tracking_rows)

    return {
        "week_number": plan.get("week_number", 1),
        "days_total": days_total,
        "days_logged": days_logged,
        "can_progress": days_logged >= days_total,
    }


def _compute_1rm_progression(week_plan: dict, tracking_rows: list[dict], user_id: str) -> dict[str, float]:
    tracking_by_day = {}
    for row in tracking_rows:
        entries = decrypt_json_payload(row.get("entries_json"), aad_context=user_id)
        tracking_by_day[row["day"]] = entries

    totals: dict[str, dict] = {i: {"prescribed": 0, "done": 0} for i in _1RM_KEYS}

    for day, exercises in week_plan.items():
        day_entries = tracking_by_day[day]
        for idx, exercise in enumerate(exercises):
            rm_key = EXERCISE_1RM_MAP.get(exercise["name"])
            if not rm_key:
                continue
            prescribed_sets = exercise["sets"]
            entry = day_entries.get(f"{day}:{idx}", {})
            sets_done = entry.get("sets_done", 0)
            totals[rm_key]["prescribed"] += prescribed_sets
            totals[rm_key]["done"] += sets_done

    multipliers = {}
    for rm_key, sets in totals.items():
        if sets["prescribed"] == 0:
            multipliers[rm_key] = 1.0
            continue
        ratio = sets["done"] / sets["prescribed"]
        if ratio < 0.50:
            multipliers[rm_key] = 0.90
        elif ratio < 0.80:
            multipliers[rm_key] = 1.0
        elif ratio < 1.00:
            multipliers[rm_key] = 1.0125
        else:
            multipliers[rm_key] = 1.05 if rm_key in ("squat_1rm", "deadlift_1rm") else 1.025

    return multipliers


@router.post("/{plan_id}/progress")
async def progress_plan(
    plan_id: str,
    user_id: str = Depends(get_current_user_id),
):
    plan = await _get_full_plan(plan_id, user_id)
    week_plan = plan["response_json"]["week_plan"]
    tracking_rows = await _get_tracking_rows(plan_id, user_id)

    multipliers = _compute_1rm_progression(week_plan, tracking_rows, user_id)

    profile = await get_profile(user_id)
    updated_1rms = {}
    for rm_key, mult in multipliers.items():
        current = profile[rm_key]
        updated_1rms[rm_key] = round(current * mult, 1)

    client = get_http_client()
    await client.patch(
        f"{SUPABASE_URL}/rest/v1/profiles",
        params={"id": f"eq.{user_id}"},
        headers=SERVICE_HEADERS,
        json=updated_1rms,
    )

    profile = await get_profile(user_id)
    request_snapshot = _build_optimiser_input(profile)

    old_week = plan.get("week_number", 1)
    plan_row = await _insert_plan(
        user_id, request_snapshot, parent_plan_id=plan_id, week_number=old_week + 1,
    )
    new_plan_id = plan_row["id"]

    try:
        result = TrainingPlanOptimiser(GeneratePlanRequest(**request_snapshot)).solve()
        result_json = result.model_dump(mode="json")

        await _update_plan(
            new_plan_id,
            {"status": "success", "response_json": result_json, "user_id": user_id},
        )
        return {"plan_id": new_plan_id}

    except InfeasiblePlanError as e:
        error_msg = str(e)
        await _update_plan(new_plan_id, {"status": "error", "error_message": error_msg})
        return {"plan_id": new_plan_id, "status": "error", "error_message": error_msg}

    except Exception:
        await _update_plan(new_plan_id, {"status": "error", "error_message": "internal error"})
        return {"plan_id": new_plan_id, "status": "error", "error_message": "internal error"}
