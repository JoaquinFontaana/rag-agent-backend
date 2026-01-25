from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Literal, Optional
from functools import lru_cache
import os

BASE_DIR = Path(__file__).resolve().parent.parent


class BaseConfig(BaseSettings):
    """Configuración base compartida por todos los entornos"""
    vector_store_path: str = str(BASE_DIR/"data"/"vectorstore")
    # API Keys
    google_api_key: str
    
    base_dir: Path = BASE_DIR

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        case_sensitive=False,
        extra="ignore"
    )


class DevelopmentConfig(BaseConfig):
    """Configuración para desarrollo"""
    debug: bool = True


class ProductionConfig(BaseConfig):
    """Configuración para producción"""
    debug: bool = False


class TestConfig(BaseConfig):
    """Configuración para testing"""
    debug: bool = True


@lru_cache()
def get_settings() -> BaseConfig:
    """
    Factory que obtiene la configuración según ENVIRONMENT del .env
    
    Lee la variable ENVIRONMENT del .env y carga la clase correspondiente:
    - development → DevelopmentConfig (default)
    - production → ProductionConfig
    - test → TestConfig
    """
    # Lee ENVIRONMENT del .env o default a development
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    configs = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "test": TestConfig,
    }
    
    config_class = configs.get(env, DevelopmentConfig)
    return config_class()


# Singleton - se configura automáticamente desde el .env
settings = get_settings()