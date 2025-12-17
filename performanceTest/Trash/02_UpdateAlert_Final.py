from locust import HttpUser, task, constant, between
from variable import write_token, my_list
import threading

class UpdateAlertRuleUser(HttpUser):
    wait_time = between(0, 0)   #simulated user will wait a random amount of time between 1 and 2 seconds
    wait_time = constant(0)

    max_requests = 10200
    request_count = 0
    request_lock = threading.Lock()

    user_counter = 0
    user_lock = threading.Lock()

    id_index = 0
    id_lock = threading.Lock()

    def on_start(self):
        # Assign a unique base name for this user
        with UpdateAlertRuleUser.user_lock:
            UpdateAlertRuleUser.user_counter += 1
            self.base_username = f"locust{UpdateAlertRuleUser.user_counter}"

    @task
    def update_alert_rule(self):
        with UpdateAlertRuleUser.request_lock:
            if UpdateAlertRuleUser.request_count >= UpdateAlertRuleUser.max_requests:
                self.environment.runner.quit()
                return
            UpdateAlertRuleUser.request_count += 1
            request_number = UpdateAlertRuleUser.request_count

        with UpdateAlertRuleUser.id_lock:
            if UpdateAlertRuleUser.id_index >= len(my_list):
                UpdateAlertRuleUser.id_index = 0
            alert_id = my_list[UpdateAlertRuleUser.id_index]
            UpdateAlertRuleUser.id_index += 1
        headers = {
            "Authorization": write_token,
            "Content-Type": "application/json"
        }

        payload = {
            "search_params": {
                "query": "user in ADMINS | chart count() ",
                "timerange_day": 0,
                "timerange_hour": 0,
                "timerange_minute": 10,
                "repos": ["127.0.0.1:5504/default"],
                "limit": 100,
                "flush_on_trigger": False,
                "search_interval_trigger": False,
                "search_interval_minute": 1,
                "delay_interval_trigger": False,
                "delay_interval_minute": 1,
                "throttling_enabled": False,
                "throttling_field": "",
                "throttling_time_range": 0
            },
            "incident_condition": {
                "condition_option": "notequal",
                "condition_value": 1,
                "risk": "medium",
                "aggregate": "avg"
            },
            "taxonomy": {
                "attack_tag_hashes": [],
                "logsources": [],
                "metadata": [
                    {
                        "field": "updatefield",
                        "value": "updatedvalue"
                    }
                ]
            },
            "incident_ownership": {
                "assignee": "admin",
                "visible_to_users": []
            },
            "incident_display_data": {
                "apply_jinja_template": True,
                "simple_view": False,
                "jinja_template": "<style type=\"text/css\">...</style>"  # Truncated for brevity
            },
            "foureyes": {
                "original_data": False
            },
            "name": f"AlertUpdate_User{self.base_username}_Req{request_number}",
            "description": f"This is the description updated one _Updated{alert_id}",
            "id": alert_id
        }

        self.client.post(
            "/AlertRules/update_api",
            json=payload,
            headers=headers,
            verify=False  # For self-signed SSL
        )

