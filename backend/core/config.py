# core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from dotenv import load_dotenv


load_dotenv()
class Settings(BaseSettings):
    API_KEY: str
    MONGO_URI: str
    CONNECTION_STRING: str
    GAME_DURATION: int = 30
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()