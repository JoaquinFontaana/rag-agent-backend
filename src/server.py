"""Local development server with custom endpoints"""
from fastapi import FastAPI
from src.app_config import configure_app
from fastapi import APIRouter
from src.controllers.document_controller import router as documents_router
from src.controllers.user_controller import router as user_router
from src.controllers.auth_controller import router as auth_router
from main import setup_logging

# Configure logging
setup_logging()

# Main router that combines all coontrollers
router = APIRouter()

router.include_router(documents_router)
router.include_router(user_router)
router.include_router(auth_router)
app = FastAPI()

# Configure app (exception handlers, middleware, etc.)
configure_app(app)

# Include custom endpoints
app.include_router(router, prefix="/api")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)