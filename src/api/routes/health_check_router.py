from fastapi import APIRouter, Response

router = APIRouter(prefix="/-/health-checks", tags=["Utils"])


@router.get("/liveness", status_code=204)
async def api_health_check_liveness():
    """/-/health-checks/liveness endpoint controller

    Should return status code 204.
    """
    return Response(status_code=204, media_type="application/json")


@router.get("/readiness", status_code=204)
async def api_health_check_readiness():
    """/-/health-checks/readiness endpoint controller

    Should return status code 204.
    """
    return Response(status_code=204, media_type="application/json")


@router.get("/sentry-debug", status_code=204)
async def api_health_check_sentry_debug():
    # This endpoint is used to test Sentry integration
    # It will raise an exception that Sentry will capture
    raise Exception("Sentry Debug Endpoint Triggered")