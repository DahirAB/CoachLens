from fastapi import APIRouter, Depends, HTTPException, Query

from ..core.auth import get_current_user_id
from ..core.config import SERVICE_HEADERS, SUPABASE_URL
from ..core.http import get_http_client
from ..models.schemas import DailyTrackingRequest

router = APIRouter(prefix="/api/plans")


async def _get_plan_for_user(plan_id: str, user_id: str) -> dict:
    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plans",
        params={"id": f"eq.{plan_id}", "user_id": f"eq.{user_id}", "select": "*"},
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch plan: {resp.text}")
    rows = resp.json()
    if not rows:
        raise HTTPException(status_code=404, detail="Plan not found")
    return rows[0]


def _validate_entries(body: DailyTrackingRequest, plan_response_json: dict) -> dict:
    week_plan = plan_response_json.get("week_plan") 
    day_str = body.day.value
    day_exercises = week_plan.get(day_str)

    if not day_exercises or len(day_exercises) == 0:
        return {}

    n = len(day_exercises)
    validated = {}

    for key, entry in body.entries.items():
        _, idx_str = key.split(":", 1)
        idx = int(idx_str)
        if idx < 0 or idx >= n:
            raise HTTPException(status_code=422, detail=f"Invalid slot index: {idx} (max {n - 1})")

        planned_sets = day_exercises[idx].get("sets", 0)
        if entry.sets_done > planned_sets:
            raise HTTPException(
                status_code=422,
                detail=f"sets_done must be 0..{planned_sets} for slot {key}",
            )

        exercise_name = day_exercises[idx].get("name", "")
        validated[key] = {
            "exercise_name": exercise_name,
            "done": entry.done,
            "sets_done": entry.sets_done,
        }

    return validated


@router.get("/{plan_id}/tracking/daily")
async def get_daily_tracking(
    plan_id: str,
    logged_date: str = Query(...),
    user_id: str = Depends(get_current_user_id),
):
    
    await _get_plan_for_user(plan_id, user_id)

    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plan_tracking_daily",
        params={
            "plan_id": f"eq.{plan_id}",
            "user_id": f"eq.{user_id}",
            "logged_date": f"eq.{logged_date}",
            "select": "*",
        },
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch tracking: {resp.text}")
    rows = resp.json()
    if not rows:
        raise HTTPException(status_code=404, detail="No tracking found for this day ")
    return rows[0]


@router.put("/{plan_id}/tracking/daily")
async def put_daily_tracking(
    plan_id: str,
    body: DailyTrackingRequest,
    user_id: str = Depends(get_current_user_id),
):
    """Upsert daily tracking. Validates entries against plan; overwrites exercise_name with plan slot."""
    plan = await _get_plan_for_user(plan_id, user_id)
    response_json = plan.get("response_json") or {}

    validated_entries = _validate_entries(body, response_json)

    payload = {
        "plan_id": plan_id,
        "user_id": user_id,
        "day": body.day.value,
        "logged_date": body.logged_date,
        "timezone": body.timezone,
        "entries_json": validated_entries,
        "note_text": body.note_text,
    }

    upsert_headers = {**SERVICE_HEADERS, "Prefer": "resolution=merge-duplicates,return=representation"}

    client = get_http_client()
    resp = await client.post(
        f"{SUPABASE_URL}/rest/v1/plan_tracking_daily",
        params={"on_conflict": "plan_id,user_id,logged_date"},
        headers=upsert_headers,
        json=payload,
    )

    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Failed to upsert tracking: {resp.text}")

    rows = resp.json()
    return rows[0] if rows else payload
