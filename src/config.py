import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # LLM
    LLM_PROVIDER: str = "groq"
    LLM_API_KEY: Optional[str] = None
    LLM_MODEL: str = "llama3-8b-8192"

    # Embeddings
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Linking
    LINK_SIM_THRESHOLD: float = 0.75
    FAISS_TOP_K: int = 5

    # RAG
    RAG_TOP_K: int = 5
    RAG_MAX_TOKENS: int = 2048

    # Graph
    GRAPH_MAX_NODES: int = 500

    # Deployment
    AUTH_REQUIRED: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def validate_setup(self):
        if not self.LLM_API_KEY:
            print("ERROR: LLM_API_KEY not set. Copy .env.example -> .env and add your key.")
            exit(1)

settings = Settings()

if __name__ == "__main__":
    import sys
    if "--check" in sys.argv:
        settings.validate_setup()
        print("Configuration OK.")
