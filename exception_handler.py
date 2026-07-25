from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


async def exception_handler(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
        },
    )