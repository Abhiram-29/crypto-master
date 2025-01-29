from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pydantic import BaseModel,Field
from typing import Optional,List


load_dotenv()
conn_uri = os.getenv("CONNECTION_STRING")

client = MongoClient(conn_uri)

try:
    database = client.get_database("CryptoMaster")
    print("HELLO")
except Exception as e:
    print(e)