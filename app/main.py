from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from app.api.v1 import api_router
from app.core.config import settings
import traceback

app = FastAPI(
    title="Agentic Backend API",
    description="AI Agent/Chatbot backend with authentication, conversation management, and message streaming.",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)


# Add global exception handler for better error messages
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions"""
    error_detail = {
        "error": type(exc).__name__,
        "message": str(exc),
        "path": str(request.url),
    }
    # Print without unicode characters for Windows console compatibility
    print(f"ERROR - Unhandled exception: {error_detail}")
    traceback.print_exc()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error_detail
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


# Add session middleware (required for OAuth state management)
app.add_middleware(
    SessionMiddleware, secret_key=settings.secret_key, max_age=3600  # 1 hour
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Agentic Backend API is running!",
        "status": "healthy",
        "version": "0.1.0",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
