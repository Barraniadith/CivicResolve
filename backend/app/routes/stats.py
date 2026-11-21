from fastapi import APIRouter
from ..database import get_stats_data
from ..schemas import StatsResponse

router = APIRouter(prefix="/api/stats", tags=["Statistics"])

@router.get("", response_model=StatsResponse)
def get_dashboard_stats():
    data = get_stats_data()
    return StatsResponse(**data)
