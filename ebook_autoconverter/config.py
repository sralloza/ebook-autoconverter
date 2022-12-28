"""Configuration module."""

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Settings for the application."""

    calibre_executable: str = "/usr/bin/ebook-convert"
    calibre_web_url: str = Field(..., env="CALIBRE_WEB_URL")
    calibre_web_username: str = Field(..., env="CALIBRE_WEB_USERNAME")
    calibre_web_password: str = Field(..., env="CALIBRE_WEB_PASSWORD")


settings = Settings()  # type: ignore
