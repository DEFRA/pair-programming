# FastAPI router for pairing logic
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from pymongo.collection import Collection

from app.common.mongo import get_db
from app.users.models import PairRequest, PairResponse, UserResponse

router = APIRouter(prefix="/pair", tags=["pair"])


@router.post("/", response_model=PairResponse)
async def pair_user(
    req: PairRequest,
    db=Depends(get_db),
):
    users: Collection = db["users"]
    user = await users.find_one({"email": req.email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    # Find a user not already paired with
    paired_with = set(user.get("paired_with", []))
    candidates = users.find(
        {
            "$and": [
                {"_id": {"$ne": user["_id"]}},
                {"_id": {"$nin": [ObjectId(paired_id) for paired_id in paired_with]}},
            ]
        }
    )
    match: Optional[dict] = None
    async for candidate in candidates:
        match = candidate
        break
    # If all pairs exhausted, allow pairing with any other user
    if not match:
        candidates = users.find({"_id": {"$ne": user["_id"]}})
        async for candidate in candidates:
            match = candidate
            break
    if not match:
        return PairResponse(
            paired_with=None, message="No other users available to pair."
        )
    # Update both users' paired_with
    await users.update_one(
        {"_id": user["_id"]}, {"$addToSet": {"paired_with": str(match["_id"])}}
    )
    await users.update_one(
        {"_id": match["_id"]}, {"$addToSet": {"paired_with": str(user["_id"])}}
    )
    # TODO: Send email via Gov Notify here
    match_response = UserResponse(
        id=str(match["_id"]),
        name=match["name"],
        email=match["email"],
        paired_with=match.get("paired_with", []),
    )
    return PairResponse(
        paired_with=match_response,
        message=f"Paired with {match['name']} ({match['email']})",
    )
