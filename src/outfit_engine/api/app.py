from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from outfit_engine.api.router import router
from outfit_engine.config.bootstrap import get_command_handler

app = FastAPI(
    title="AI Outfit Bundle Recommendation Engine",
    description="Category- and gender-agnostic outfit recommendation system",
    version="1.0.0",
)

app.include_router(router)


@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "code": "VALIDATION_ERROR",
            "message": str(exc),
            "retryable": False,
        },
    )


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "code": "VALIDATION_ERROR",
            "message": str(exc),
            "retryable": False,
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "code": "INTERNAL",
            "message": "An internal error occurred",
            "retryable": True,
        },
    )


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {
        "service": "AI Outfit Bundle Recommendation Engine",
        "version": "1.0.0",
        "status": "running",
    }
