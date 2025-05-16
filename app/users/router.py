# FastAPI router for user registration and listing
from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.collection import Collection

from app.common.mongo import get_db
from app.users.models import UserRegisterRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user: UserRegisterRequest,
    db=Depends(get_db),
):
    users: Collection = db["users"]
    existing = await users.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=400, detail="User already registered.")
    user_doc = {
        "name": user.name,
        "email": user.email,
        "paired_with": [],
    }
    result = await users.insert_one(user_doc)
    user_doc["id"] = str(result.inserted_id)
    return UserResponse(
        id=user_doc["id"],
        name=user_doc["name"],
        email=user_doc["email"],
        paired_with=[],
    )


@router.get("/", response_model=list[UserResponse])
async def list_users(db=Depends(get_db)):
    users: Collection = db["users"]
    cursor = users.find()
    result = []
    async for user in cursor:
        result.append(
            UserResponse(
                id=str(user["_id"]),
                name=user["name"],
                email=user["email"],
                paired_with=user.get("paired_with", []),
            )
        )
    return result
