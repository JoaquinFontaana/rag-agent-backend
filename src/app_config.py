"""Application configuration for LangSmith deployment"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.errors.handlers import setup_exception_handlers
import logging

logger = logging.getLogger(__name__)

def configure_app(app: FastAPI) -> None:
    """
    Configure the FastAPI application with handlers, middleware, etc.
    This is called by LangSmith during deployment.
    """
    logger.info("Configuring FastAPI application...")
    
    # Setup CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000", "http://localhost:3001"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Setup exception handlers
    setup_exception_handlers(app)
    
    logger.info("Application configured successfully")
