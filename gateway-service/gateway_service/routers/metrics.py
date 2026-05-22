from fastapi import APIRouter

from gateway_service.metrics import metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def get_metrics():
    return metrics.snapshot()
