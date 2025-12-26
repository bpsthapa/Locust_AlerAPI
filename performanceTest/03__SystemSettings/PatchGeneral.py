from locust import HttpUser, task, constant
import threading
import logging
from performanceTest.TestData.ConfigAPI_78 import *

# ---------- Custom Logger (Locust-safe) ----------
logger = logging.getLogger("system_settings_update_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler("performanceTest/03__SystemSettings/TerminalOutput/system_settings.log", mode="a")
stream_handler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s | %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.propagate = False  # Prevent Locust from overriding this logger


class SystemSettingsUser(HttpUser):
    wait_time = constant(0)
    max_requests = 10000
    request_count = 0
    user_count = 0
    lock = threading.Lock()

    def on_start(self):
        # Assign unique user number
        with SystemSettingsUser.lock:
            SystemSettingsUser.user_count += 1
            self.user_number = SystemSettingsUser.user_count

    @task
    def update_system_settings(self):
        # Stop test after max_requests
        with SystemSettingsUser.lock:
            if SystemSettingsUser.request_count >= SystemSettingsUser.max_requests:
                # Flush logs before quitting
                for handler in logger.handlers:
                    handler.flush()
                self.environment.runner.quit()
                return

            SystemSettingsUser.request_count += 1
            current_request = SystemSettingsUser.request_count

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": wite_token
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
                msg = (
                    f"User #{self.user_number} | "
                    f"Request #{current_request} | "
                    f"FAILED | Status: {response.status_code} | Response: {response.text}"
                )
                logger.error(msg)
                response.failure(msg)
            else:
                msg = (
                    f"User #{self.user_number} | "
                    f"Request #{current_request} | "
                    f"SUCCESS | Status: {response.status_code}"
                )
                logger.info(msg)
                print(msg)
                response.success()


#locust -f performanceTest/03__SystemSettings/PatchGeneral.py --host=https://10.45.3.78