import time
from datetime import datetime

from fastapi import APIRouter

from app.utils.time_format import format_date, format_duration

router = APIRouter(tags=["Health"])
startup_time = datetime.now()
process_start = time.time()


@router.get("/health")
async def get_health() -> dict:
    now = datetime.now()
    uptime_seconds = time.time() - process_start
    return {
        "Status": "✅ YTRC Center API running!",
        "Project": "YTRC Center",
        "Startup Time": format_date(startup_time),
        "Uptime": format_duration(uptime_seconds),
        "Server Time": format_date(now),
        "Redis Status": "⚠️ Not Configured",
        "Online Users (Real-time)": 0,
    }


@router.get("/health/smoke-test")
async def smoke_test() -> dict:
    return {"status": "OK", "version": "1.0.1", "timestamp": datetime.now().isoformat()}
