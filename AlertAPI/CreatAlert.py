from locust import HttpUser, task, between
from variable import *

class LoadTestUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def create_alert_rule(self):
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
                "repos": [
                    "127.0.0.1:5504/ASE",
                    "127.0.0.1:5504/default",
                    "127.0.0.1:5504/_logpoint"
                ],
                "limit": 1000000,
                "flush_on_trigger": True,
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
                "original_data": True
            },
            "name": "locust",
            "description": "जस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तैजस्तै"
        }

        self.client.post("/AlertRules/create_api", json=payload, headers=headers, verify=False)
