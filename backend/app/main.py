from fastapi import FastAPI, Response, status

from app.db import check_database

app = FastAPI(title="Cost Inventory API")


@app.get("/health")
def health(response: Response) -> dict[str, str]:
    try:
        check_database()
    except Exception:  # noqa: BLE001 - legacy health must return a safe 503
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "unhealthy", "database": "unavailable"}

    return {"status": "ok", "database": "ok"}
