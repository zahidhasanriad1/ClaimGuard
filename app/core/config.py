from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ClaimGuard"
    debug: bool = True
    host: str = "127.0.0.1"
    port: int = 8000
    gemini_api_key: str = ""
    raw_docs_dir: Path = Path("data/raw")
    pages_dir: Path = Path("data/pages")
    parsed_docs_dir: Path = Path("data/parsed")
    ocr_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


def ensure_directories() -> None:
    settings.raw_docs_dir.mkdir(parents=True, exist_ok=True)
    settings.pages_dir.mkdir(parents=True, exist_ok=True)
    settings.parsed_docs_dir.mkdir(parents=True, exist_ok=True)