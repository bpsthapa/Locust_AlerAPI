from locust import HttpUser, task, between
import random
import string
resourceUrl="/getalloweddata"


class GetTimeZone(HttpUser):
    wait_time = between(1, 2)
    host = "https:10.45.10.47"  # Add this line
   
    @task
    def add_book(self):        
        payload = {
            "username" : "admin",
            "secret_key" : "16484665d08835f2826e88c4b4383417",
            "type" : "user_preference"
        }

        headers = {"Content-Type": "application/json"}
        response = self.client.post(resourceUrl, json=payload, headers=headers)

        #Validation
        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Failed with status code: {response.status_code}")
