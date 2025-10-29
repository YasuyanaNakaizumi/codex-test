from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    azure_openai_endpoint: str = Field(..., env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(..., env="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(
        default="2024-05-01-preview", env="AZURE_OPENAI_API_VERSION"
    )
    azure_openai_deployment: str = Field(..., env="AZURE_OPENAI_DEPLOYMENT")
    azure_openai_embedding_deployment: str = Field(
        ..., env="AZURE_OPENAI_EMBEDDING_DEPLOYMENT"
    )
    chunk_size: int = Field(
        750,
        description="Character length of document chunks.",
        env="CHUNK_SIZE",
    )
    chunk_overlap: int = Field(
        150,
        description="Overlap between chunks to preserve context.",
        env="CHUNK_OVERLAP",
    )
    faiss_index_path: Optional[str] = Field(
        default="data/faiss_index",
        description="Directory where FAISS index is stored.",
        env="FAISS_INDEX_PATH",
    )

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()
