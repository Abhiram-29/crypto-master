# core/config.py
from pydantic import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv("../.env")
class Settings(BaseSettings):
    API_KEY: str
    MONGO_URI: str
    GAME_DURATION: int = 30

    class Config:
        env_file = "../.env"
        env_file_encoding = 'utf-8'
