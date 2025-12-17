from locust import HttpUser, task, between, constant
from variable import *
import threading

class LoadTestUser(HttpUser):
    wait_time = between(0, 1)   #simulated user will wait a random amount of time between 1 and 2 seconds
    wait_time = constant(0)   #no any delay between request

    max_requests = 3000      #the testing will stop after 1000 request
    request_count = 0
    request_lock = threading.Lock()
    user_counter = 0
    user_lock = threading.Lock()

    def on_start(self):
        # Assign a unique base name for this user
        with LoadTestUser.user_lock:
            LoadTestUser.user_counter += 1
            self.base_username = f"locust{LoadTestUser.user_counter}"

    @task
    def create_alert_rule(self):
        with LoadTestUser.request_lock:
            if LoadTestUser.request_count >= LoadTestUser.max_requests:
                self.environment.runner.quit()  # Stop the test
                return
            LoadTestUser.request_count += 1
            request_id = LoadTestUser.request_count

        headers = {
            "Authorization": write_token,
            "Content-Type": "application/json"
        }

        payload = {
            "search_params": {
                "query": "case_id=* case_status=* case_severity=* norm_id=SOAR | latest by case_id | search case_status!=Closed | rename case_severity as sv | chart count(sv>30 and sv<=60) as Medium, count(sv>60 and sv<=80) as High, count(sv>80) as Critical",
                "timerange_day": 0,
                "timerange_hour": 0,
                "timerange_minute": 10,
                "repos": 

[
"127.0.0.1:5504/AlertR133",
"127.0.0.1:5504/Proxy_WAF",
"127.0.0.1:5504/Dumy",
"127.0.0.1:5504/Repo133",
"127.0.0.1:5504/SiteA",
"127.0.0.1:5504/SiteA-subsite",
"127.0.0.1:5504/UEBA_730",
"127.0.0.1:5504/benchmark",
"127.0.0.1:5504/cisco",
"127.0.0.1:5504/ueba",
"127.0.0.1:5504/ueba_op",
"127.0.0.1:5504/security",
"127.0.0.1:5504/cloud",
"127.0.0.1:5504/agileSI",
"127.0.0.1:5504/uebaoutput",
"127.0.0.1:5504/windows",
"127.0.0.1:5504/firewalls"

]


                ,
                "limit": 1000000,
                "flush_on_trigger": False,
                "search_interval_trigger": True,
                "search_interval_minute": 1,
                "delay_interval_trigger": True,
                "delay_interval_minute": 11,
                "throttling_enabled": True,
                "throttling_field": "user",
                "throttling_time_range": 1
            },
            "incident_condition": {
                "condition_option": "lessthan",
                "condition_value": 10,
                "risk": "low",
                "aggregate": "max"
            },
            "taxonomy": {
                "attack_tag_hashes": [],
                "logsources": [
                    "AWS Cloudtrail",
                    "Antivirus",
                    "Barracuda",
                    "Cisco FWSM",
                    "Cisco",
                    "Webserver",
                    "WAF1"
                ],
                "metadata": [
                    {
                        "field": "string",
                        "value": "string"
                    }
                ]
            },
            "incident_ownership": {
                "assignee": "admin",
                "visible_to_users": []
            },
            "incident_display_data": {
                "apply_jinja_template": True,
                "simple_view": True,
                "jinja_template": "hello"
            },
            "foureyes": {
                "original_data": False
            },

            "name": f"BPNThapaaa_{LoadTestUser.user_counter}_Request{request_id}",
            "description": "Hello This is alert"
        }

        self.client.post("/AlertRules/create_api", json=payload, headers=headers, verify=False)




#locust -f AlertAPI/01_CreatAlert_Final.py --host=https://10.45.3.140 --users 1 --spawn-rate 1
#this is the workinone