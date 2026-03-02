from fastapi import APIRouter

router = APIRouter(prefix="/access-control", tags=["Access Control"])


@router.get("/apps")
async def get_apps():
    return []


@router.get("/apps/{app_name}/users")
async def get_app_users(app_name: str):
    return []


@router.post("/apps/{app_name}/users")
async def assign_permission(app_name: str, body: dict):
    return {"message": "Permission assigned - to be implemented"}


@router.delete("/apps/{app_name}/users/{user_id}")
async def remove_permission(app_name: str, user_id: str):
    return {"message": "Permission removed - to be implemented"}
