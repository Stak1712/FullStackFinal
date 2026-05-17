from fastapi import APIRouter, HTTPException, status

router = APIRouter()

@router.get("/next")
async def next_question():
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")
