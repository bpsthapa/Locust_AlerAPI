from locust import HttpUser, task, constant
from locust.exception import StopUser
import threading
import logging
import urllib3

from performanceTest.TestData.ConfigAPI_78 import *

# -----------------------------
# Disable SSL warnings (internal env only)
# -----------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------
# Custom Logger
# -----------------------------
logger = logging.getLogger("patch_system_settings_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(
        "performanceTest/03__SystemSettings/TerminalOutput/patch_system_settings.log",
        mode="a"
    )
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

logger.propagate = False


class PatchSystemSettingsUser(HttpUser):
    wait_time = constant(0)

    # ----- Global counters -----
    max_requests = 5000
    request_count = 0
    user_count = 0
    lock = threading.Lock()

    def on_start(self):
        with PatchSystemSettingsUser.lock:
            PatchSystemSettingsUser.user_count += 1
            self.user_number = PatchSystemSettingsUser.user_count

    @task
    def patch_system_settings(self):
        with PatchSystemSettingsUser.lock:
            if PatchSystemSettingsUser.request_count >= PatchSystemSettingsUser.max_requests:
                raise StopUser()

            PatchSystemSettingsUser.request_count += 1
            current_request = PatchSystemSettingsUser.request_count

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": write_token
        }

        payload = {
            "name": f"BipinSH_{current_request}_{self.user_number}",
            "tab_title": "MileStone2",
            "ip_dns": "10.3.4.2",
            "default_auth": "LogpointAuthentication",
            "timeout": 1339,
            "default_ha_path": "/opt/immune/storage",
            "timestamp_on": "log_ts",
            "overscan_period": 20,
            "timezone": "Europe/Helsinki",
            "enable_soar": "false",
            "share_usage_data": "TRUE",
            "request_timeout": 20
        }

        with self.client.patch(
            "/api/v1/system-settings",
            headers=headers,
            json=payload,
            verify=False,
            catch_response=True
        ) as response:

            if response.status_code != 200:
                msg = (
                    f"User #{self.user_number} | "
                    f"Request #{current_request} | "
                    f"FAILED | Status: {response.status_code}"
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
                response.success()

#locust -f performanceTest/03__SystemSettings/patchGeneral_1.py --host=https://10.45.12.32