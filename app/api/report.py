from fastapi import APIRouter
from ..utils.helpers import detections_history

router = APIRouter()


@router.get("/api/report")
def report():
    report = "\n".join(detections_history) or "No alerts yet."
    detections_history.clear()
    return {
        "message": "Report generated",
        "count": len(report.splitlines())
    }
