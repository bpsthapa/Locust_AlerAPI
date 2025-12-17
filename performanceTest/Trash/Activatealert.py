from locust import HttpUser, task, between
from variable import *
import warnings
import urllib3

# Ignore SSL certificate warnings for self-signed certificates
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

class LoadTestUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def activate_alert_rule(self):
        headers = {
            "Authorization": write_token,
            "Content-Type": "application/json"
        }

        payload = {
            "ids": ["681c45ded66bbc40016a3af4"]
        }

        self.client.post(
            "/AlertRules/activate_api",
            headers=headers,
            json=payload,
            verify=False
        )
