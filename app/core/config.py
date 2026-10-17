import os
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_NAME: str = "MedTrail"
    APP_ENV: str = "development"
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"

    # Neo4j Settings
    NEO4J_URI: str = Field(default="neo4j+s://7743778d.databases.neo4j.io")
    NEO4J_USERNAME: str = Field(default="7743778d")
    NEO4J_PASSWORD: str = Field(default="H-iKJxoJV49_7jVHhHKLg2mTW7Si6ZraO0fLkSf760E")
    NEO4J_DATABASE: str = Field(default="7743778d")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
