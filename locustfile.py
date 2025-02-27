from locust import HttpUser, task, between
from dotenv import load_dotenv
import os
import random

load_dotenv()
api_key = os.getenv("API_KEY")

print(f"API Key loaded: {api_key}")
class APIUser(HttpUser):
    wait_time = between(2,5)

    @task(3)
    def ask_question(self):
        user_id = 'A1'
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
    
    @task
    def login(self):
        user_id = "A1"  # Make sure this is different from "ABCD123"
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
    @task(3)
    def update(self):
        user_id = "A1"
        question_id = 4
        spent_amt = 10
        mulitplier = 1
        time_left = 1500
        solve = True
        print(f"Sending update request")
        headers = {
            "API_KEY": api_key,
            "Content-Type":"application/json"
        }
        payload = {
        "user_id": user_id,
        "question_id": question_id,
        "spent_amt": spent_amt,
        "multiplier": mulitplier,
        "time_left": time_left,
        "solved": solve
        }

        with self.client.post("/update",headers=headers,json=payload,catch_response=True) as response:
            if response.status_code == 200:
                pass
            else:
                response.failure(f"Request failed with status code: {response.status_code}, Resoponse: {response.text}")
    
    @task(4)
    def questionStart(self):
        user_id = "A1"
        question_id = 4
        bet_amt = 1
        time_left = 1500

        headers = {
            "API_KEY": api_key,
            "Content-Type":"application/json"
        }
        payload = {
            "user_id": user_id,
            "question_id": question_id,
            "bet_amt": bet_amt,
            "time_left": time_left
        }

        with self.client.post("/questionStart",headers=headers,json=payload,catch_response=True) as response:
            if response.status_code == 200:
                pass
            else:
                response.failure(f"Request failed with status code: {response.status_code}, Resoponse: {response.text}")