from locust import HttpUser, task, between
import warnings
import urllib3
from variable import *

# Suppress SSL certificate warnings
warnings.filterwarnings("ignore", category=urllib3.exceptions.InsecureRequestWarning)

class LoadTestUser(HttpUser):
    wait_time = between(1, 2)  # Simulate user think time

    @task
    def get_alert_rules_list(self):
        headers = {
            "Authorization": read_token
        }

        self.client.get("/AlertRules/lists_api", headers=headers, verify=False)
