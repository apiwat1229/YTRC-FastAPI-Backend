from fastapi import APIRouter

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/stats")
async def get_stats():
    return {
        "totalUsers": 0,
        "totalBookings": 0,
        "totalPools": 0,
        "message": "Analytics stats - to be implemented",
    }
