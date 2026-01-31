from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("", summary="Health Check", description="Check if the service is active")
def healt_check():
    return {"message": "Service is active"}