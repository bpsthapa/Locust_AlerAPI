from locust import HttpUser, task, between
import json
import threading

class MyUser(HttpUser):
    wait_time = between(2, 4)
    
    # Shared counters
    max_requests = 100
    request_count = 0
    request_lock = threading.Lock()
    user_counter = 0  # to assign user IDs

    def on_start(self):
        # Unique user ID
        with MyUser.request_lock:
            MyUser.user_counter += 1
            self.user_id = MyUser.user_counter
        self.local_request_counter = 0

    @task
    def update_alert_rule(self):
        # Lock before accessing shared request count
        with MyUser.request_lock:
            if MyUser.request_count >= MyUser.max_requests:
                self.environment.runner.quit()  # Stop the whole test
                return
            MyUser.request_count += 1
            self.local_request_counter += 1
            current_count = MyUser.request_count

        #dynamic_name = f"AlertNameUpdated_U{self.user_id}_R{self.local_request_counter}"
        dynamic_name = f"AlertNameUpdated_U{self.user_id}_R{self.local_request_counter}_TotalR{current_count}"

        headers = {
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsInNjb3BlIjoidXNlcjp3cml0ZSBhbGVydHJ1bGVzOndyaXRlIiwiaWF0IjoxNzQ5NjMyMjM5LCJleHAiOjE4MjE2Mjg2MzksImlzcyI6InNlbGYtc2lnbmVkIn0.THRV0PlAFjluK6KfsyG9fzDN6C108wRxasrQedvlWRg",
            "Content-Type": "application/json"
        }

        payload = {
            "search_params": {
                "query": "user=*",
                "timerange_day": 0,
                "timerange_hour": 0,
                "timerange_minute": 1,
                "repos": ["127.0.0.1:5504/default"],
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
                "metadata": [{"field": "string", "value": "string"}]
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
            "name": dynamic_name,
            "description": "",
            "id": "68493c3ce4dbde63e7ebab38"
        }

        print(f"working for the AlertName:  ------------------   {dynamic_name}   ---------") 
        self.client.post("/AlertRules/update_api", headers=headers, data=json.dumps(payload), verify=False)
        print(f"Completed request for AlertName: *************    {dynamic_name}   ***************")
