from locust import HttpUser, task, between
from variable import *
import warnings
import urllib3

# Suppress SSL warnings for self-signed certificates
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

class LoadTestUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def read_alert_rule(self):
        headers = {
            "Authorization": read_token
        }

        self.client.post(
            "/AlertRules/read_api?id=681c45ded66bbc40016a3af4",
            headers=headers,
            verify=False
        )
