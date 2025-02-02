import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("API_KEY")


headers = {"API_KEY": API_KEY}
response = requests.get("http://127.0.0.1:8000/login/ABCD123", headers=headers)
print(response.status_code, response.json())
