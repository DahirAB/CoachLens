from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from ..core.auth import get_current_user_id
from ..core.config import SERVICE_HEADERS, SUPABASE_URL
from ..core.crypto import decrypt_json_payload
from ..core.http import get_http_client
from ..models.schemas import (
    CreateShareRequest,
    OutgoingShare,
    SharedPlanDetail,
    SharedPlanSummary,
    ShareResponse,
)

router = APIRouter(prefix="/api/plans")


def _to_iso_z(value):
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return str(value)


def _is_expired(expires_at: str | None) -> bool:
    if not expires_at:
        return False
    dt = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt <= datetime.now(timezone.utc)


async def _get_plan_owned_by_user(plan_id: str, user_id: str) -> dict:
    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plans",
        params={
            "id": f"eq.{plan_id}",
            "user_id": f"eq.{user_id}",
            "select": "id,user_id,status,request_json,response_json,created_at",
            "limit": "1",
        },
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch plan: {resp.text}")
    row = resp.json()
    if not row:
        raise HTTPException(status_code=404, detail="Plan not found")
    return row[0]


async def _username_to_id(username: str) -> dict:
    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/profiles",
        params={
            "username": f"eq.{username}",
            "select": "id,username",
            "limit": "1",
        },
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch user")
    row = resp.json()
    if not row:
        raise HTTPException(status_code=404, detail="User not found or cannot receive shares")
    return row[0]


async def _get_valid_share(share_id: str, recipient_id: str) -> dict:
    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plan_shares",
        params={
            "id": f"eq.{share_id}",
            "select": "*",
            "limit": "1",
        },
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch share")

    row = resp.json()
    if not row:
        raise HTTPException(status_code=404, detail="Share not found")

    share = row[0]
    if share.get("recipient_id") != recipient_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if share.get("revoked_at") is not None:
        raise HTTPException(status_code=404, detail="Share not found")
    if _is_expired(share.get("expires_at")):
        raise HTTPException(status_code=404, detail="Share not found")
    return share


@router.post("/{plan_id}/share", response_model=ShareResponse)
async def create_share(
    plan_id: str,
    body: CreateShareRequest,
    user_id: str = Depends(get_current_user_id),
):
    plan = await _get_plan_owned_by_user(plan_id, user_id)
    if plan.get("status") != "success":
        raise HTTPException(status_code=400, detail="Only successful plans can be shared")

    recipient = await _username_to_id(body.username)

    recipient_id = recipient["id"]
    if recipient_id == user_id:
        raise HTTPException(status_code=400, detail="You cannot share a plan with yourself")

    payload = {
        "plan_id": plan_id,
        "owner_id": user_id,
        "recipient_id": recipient_id,
        "can_view_tracking": body.can_view_tracking,
        "expires_at": body.expires_at,
    }

    client = get_http_client()
    resp = await client.post(
        f"{SUPABASE_URL}/rest/v1/plan_shares",
        headers=SERVICE_HEADERS,
        json=payload,
    )
    if resp.status_code == 409:
        raise HTTPException(status_code=409, detail="Already shared with this user")
    if resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail=f"Failed to create share: {resp.text}")

    row = resp.json()[0]
    return ShareResponse(
        id=row["id"],
        plan_id=row["plan_id"],
        recipient_username=recipient["username"],
        can_view_tracking=row.get("can_view_tracking", False),
        expires_at=_to_iso_z(row.get("expires_at")),
        created_at=_to_iso_z(row.get("created_at")),
    )


@router.get("/shared-with-me", response_model=list[SharedPlanSummary])
async def shared_with_me(user_id: str = Depends(get_current_user_id)):
    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plan_shares",
        params={
            "recipient_id": f"eq.{user_id}",
            "revoked_at": "is.null",
            "select": "id,plan_id,owner_id,can_view_tracking,expires_at,created_at",
            "order": "created_at.desc",
        },
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch shares")

    rows = resp.json()
    active_rows = [row for row in rows if not _is_expired(row.get("expires_at"))]
    if not active_rows:
        return []

    owner_ids = {a_row["owner_id"] for a_row in active_rows}
    plan_ids = {a_row["plan_id"] for a_row in active_rows}

    owners_resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/profiles",
        params={
            "id": f"in.({','.join(owner_ids)})",
            "select": "id,username",
        },
        headers=SERVICE_HEADERS,
    )
    if owners_resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch share owners")
    owners_dict = {o_row["id"]: o_row for o_row in owners_resp.json()}

    plans_resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plans",
        params={
            "id": f"in.({','.join(plan_ids)})",
            "select": "id,created_at",
        },
        headers=SERVICE_HEADERS,
    )
    if plans_resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch shared plans")
    plans_dict = {p_row["id"]: p_row for p_row in plans_resp.json()}

    summaries: list[SharedPlanSummary] = []
    for a_row in active_rows:
        owner = owners_dict.get(a_row["owner_id"], {})
        owner_username = owner.get("username")
        if not owner_username:
            raise HTTPException(status_code=500, detail="Owner profile missing username")
        plan = plans_dict.get(a_row["plan_id"], {})
        summaries.append(
            SharedPlanSummary(
                share_id=a_row["id"],
                plan_id=a_row["plan_id"],
                owner_username=owner_username,
                can_view_tracking=a_row.get("can_view_tracking", False),
                expires_at=_to_iso_z(a_row.get("expires_at")),
                shared_at=_to_iso_z(a_row.get("created_at")),
                plan_created_at=_to_iso_z(plan.get("created_at")),
            ),
        )
    return summaries


@router.get("/shared-by-me", response_model=list[OutgoingShare])
async def shared_by_me(user_id: str = Depends(get_current_user_id)):
    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plan_shares",
        params={
            "owner_id": f"eq.{user_id}",
            "select": "id,plan_id,recipient_id,can_view_tracking,expires_at,revoked_at,created_at",
            "order": "created_at.desc",
        },
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch outgoing shares")

    rows = resp.json()
    if not rows:
        return []

    recipient_ids = {row["recipient_id"] for row in rows}
    recipients_resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/profiles",
        params={
            "id": f"in.({','.join(recipient_ids)})",
            "select": "id,username",
        },
        headers=SERVICE_HEADERS,
    )
    if recipients_resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch recipients")
    recipients_map = {row["id"]: row for row in recipients_resp.json()}

    shares: list[OutgoingShare] = []
    for row in rows:
        recipient = recipients_map.get(row["recipient_id"], {})
        shares.append(
            OutgoingShare(
                id=row["id"],
                plan_id=row["plan_id"],
                recipient_username=recipient.get("username"),
                can_view_tracking=row.get("can_view_tracking", False),
                expires_at=_to_iso_z(row.get("expires_at")),
                revoked_at=_to_iso_z(row.get("revoked_at")),
                created_at=_to_iso_z(row.get("created_at")),
            ),
        )
    return shares


@router.delete("/shares/{share_id}")
async def revoke_share(
    share_id: str,
    user_id: str = Depends(get_current_user_id),
):
    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plan_shares",
        params={"id": f"eq.{share_id}", "select": "*", "limit": "1"},
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch share")
    rows = resp.json()
    if not rows:
        raise HTTPException(status_code=404, detail="Share not found")

    share = rows[0]
    if share.get("owner_id") != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    if share.get("revoked_at") is not None:
        raise HTTPException(status_code=409, detail="Share already revoked")

    revoke_resp = await client.patch(
        f"{SUPABASE_URL}/rest/v1/plan_shares",
        params={"id": f"eq.{share_id}"},
        headers=SERVICE_HEADERS,
        json={"revoked_at": datetime.now(timezone.utc).isoformat()},
    )
    if revoke_resp.status_code not in (200, 201):
        raise HTTPException(status_code=502, detail="Failed to revoke share")
    return {"revoked": True}


@router.get("/shares/{share_id}", response_model=SharedPlanDetail)
async def get_shared_plan(
    share_id: str,
    user_id: str = Depends(get_current_user_id),
):
    share = await _get_valid_share(share_id, user_id)
    client = get_http_client()
    plan_resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plans",
        params={
            "id": f"eq.{share['plan_id']}",
            "select": "id,request_json,response_json,user_id,created_at",
            "limit": "1",
        },
        headers=SERVICE_HEADERS,
    )
    if plan_resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch shared plan")
    plan_rows = plan_resp.json()
    if not plan_rows:
        raise HTTPException(status_code=404, detail="Shared plan not found")
    plan = plan_rows[0]
    owner_id = share.get("owner_id")
    try:
        plan["request_json"] = decrypt_json_payload(plan.get("request_json"), aad_context=owner_id)
        plan["response_json"] = decrypt_json_payload(plan.get("response_json"), aad_context=owner_id)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Failed to decrypt plan data: {e}")

    owner_resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/profiles",
        params={"id": f"eq.{share['owner_id']}", "select": "username", "limit": "1"},
        headers=SERVICE_HEADERS,
    )
    if owner_resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch owner")
    owner_rows = owner_resp.json()
    if not owner_rows or not owner_rows[0].get("username"):
        raise HTTPException(status_code=500, detail="Owner missing username")
    owner_username = owner_rows[0]["username"]

    return SharedPlanDetail(
        share_id=share["id"],
        plan_id=plan["id"],
        owner_username=owner_username,
        can_view_tracking=share.get("can_view_tracking", False),
        request_json=plan.get("request_json") or {},
        response_json=plan.get("response_json") or {},
        shared_at=_to_iso_z(share.get("created_at")),
        expires_at=_to_iso_z(share.get("expires_at")),
        plan_created_at=_to_iso_z(plan.get("created_at")),
    )



@router.get("/shares/{share_id}/tracking/all")
async def get_shared_plan_tracking_all(
    share_id: str,
    user_id: str = Depends(get_current_user_id),
):
    share = await _get_valid_share(share_id, user_id)
    if not share.get("can_view_tracking", False):
        raise HTTPException(status_code=403, detail="Tracking not permitted for this share")

    client = get_http_client()
    resp = await client.get(
        f"{SUPABASE_URL}/rest/v1/plan_tracking_daily",
        params={
            "plan_id": f"eq.{share['plan_id']}",
            "user_id": f"eq.{share['owner_id']}",
            "select": "*",
            "order": "logged_date.asc",
        },
        headers=SERVICE_HEADERS,
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to fetch tracking")
    rows = resp.json()
    try:
        for row in rows:
            row["entries_json"] = decrypt_json_payload(
                row.get("entries_json"),
                aad_context=share.get("owner_id"),
            )
    except ValueError as e:
        raise HTTPException(status_code=500, detail=f"Failed to decrypt tracking data: {e}")
    return rows




