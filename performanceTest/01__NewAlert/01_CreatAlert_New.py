from locust import HttpUser, task, between, constant

#from ..variable import *
from AlertAPI.variable import *

import threading

class LoadTestUser(HttpUser):
    wait_time = between(0, 0)   #simulated user will wait a random amount of time between 1 and 2 seconds
    wait_time = constant(0)   #no any delay between request

    max_requests = 5000      #the testing will stop after 1000 request
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

        payload =  {
        "search_params": {
            "query": "case_id=* case_status=* case_severity=* norm_id=SOAR | latest by case_id | search case_status!=Closed | rename case_severity as sv | chart count(sv>30 and sv<=60) as Medium, count(sv>60 and sv<=80) as High, count(sv>80) as Critical",
            "timerange_day": 0,
            "timerange_hour": 0,
            "timerange_minute": 11,
            "repos": [
                        '10.206.76.1:5504/Alert189',
                        '10.206.76.1:5504/AlertRules189',
                        '10.206.76.1:5504/Repo189',
                        '10.206.76.1:5504/_logpoint',
                        '10.206.76.1:5504/default',
                        '10.65.220.1:5504/Alert139',
                        '10.65.220.1:5504/AlertRules139',
                        '10.65.220.1:5504/Repo130',
                        '10.65.220.1:5504/_LogPointAlerts',
                        '127.0.0.1:5504/default',
                        '127.0.0.1:5504/Repo133',
                        '127.0.0.1:5504/AlertR133'
            ],
            "limit": 100,
            "flush_on_trigger": False,
            "search_interval_minute": 1,
            "delay_interval_minute": 0,
            "throttling_enabled": False,
            "throttling_field": "",
            "throttling_time_range": 0
        },
        "incident_condition": {
            "condition_option": "greaterthan",
            "condition_value": 0,
            "risk": "low",
            "aggregate": "max"
        },
        "taxonomy": {
            "attack_tag_hashes": [],
            "logsources": [],
            "metadata": [
            {
                "field": "string",
                "value": "string"
            }
            ]
        },
        "incident_ownership": {
            "assignee": "admin",
            "visible_to_usergroups": []
        },
        "incident_display_data": {
            "apply_jinja_template": False,
            "simple_view": False,
            "jinja_template": ""
        },
        "foureyes": {
            "original_data": False
        },

            "name": f"Bps_{LoadTestUser.user_counter}_Request{request_id}",
            "description": "जस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तै"
        }

        self.client.post("/AlertRules/create_api", json=payload, headers=headers, verify=False)




#locust -f ./AlertAPI/CreatAlert_Final.py --host=https://10.45.3.136 --users 1 --spawn-rate 1