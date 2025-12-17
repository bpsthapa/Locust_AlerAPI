from locust import HttpUser, task, constant
import threading

class SystemSettingsUser(HttpUser):
    wait_time = constant(0)

    max_requests = 1000
    request_count = 0
    lock = threading.Lock()

    @task
    def update_system_settings(self):
        with SystemSettingsUser.lock:
            if SystemSettingsUser.request_count >= SystemSettingsUser.max_requests:
                self.environment.runner.quit()
                return
            SystemSettingsUser.request_count += 1

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }

        payload = {
            "name": "logpointAWS",
            "tab_title": "BIPIN",
            "ip_dns": "10.4.4.4",
            "default_auth": "LogpointAuthentication",
            "timeout": 10,
            "default_ha_path": "/opt/immune/storage",
            "timestamp_on": "log_ts",
            "overscan_period": 20,
            "timezone": "Europe/Helsinki",
            "enable_soar": False,
            "share_usage_data": True,
            "request_timeout": 20,
            "logo": "Bipin"
        }

        with self.client.patch(
            "/api/v1/system-settings",
            json=payload,
            headers=headers,
            verify=False,
            catch_response=True
        ) as response:
            if response.status_code != 200:
                response.failure(
                    f"Failed with status {response.status_code}: {response.text}"
                )
            else:
                response.success()
