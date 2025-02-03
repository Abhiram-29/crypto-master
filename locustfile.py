from locust import HttpUser, task, between
from dotenv import load_dotenv
import os
import random

load_dotenv()
api_key = os.getenv("API_KEY")

print(f"API Key loaded: {api_key}")
class APIUser(HttpUser):
    wait_time = between(5,10)

    @task
    def ask_question(self):
        user_id = '1'
        headers = {
            "API_KEY": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "user_id": user_id
        }

        with self.client.post("/questions", headers=headers, json=payload, catch_response=True) as response:
            if response.status_code == 200:
                pass
            else:
                response.failure(f"Request failed with status code: {response.status_code}, Response: {response.text}")
    
    @task(2)
    def login(self):
        user_id = "XYZ456"  # Make sure this is different from "ABCD123"
        print(f"Sending login request with user_id: {user_id}")
        headers = {
            "API_KEY": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "user_id": user_id
        }

        with self.client.post("/login",headers=headers,json=payload,catch_response=True) as response:
            if response.status_code == 200:
                pass
            else:
                response.failure(f"Request failed with status code: {response.status_code}, Response: {response.text}")