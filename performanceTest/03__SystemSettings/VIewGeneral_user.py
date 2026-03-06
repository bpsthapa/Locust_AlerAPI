from locust import HttpUser, task, constant
from locust.exception import StopUser
import threading
import logging
import urllib3

from performanceTest.TestData.ConfigAPI_78 import *

# -----------------------------
# Disable SSL Warning (internal env only)
# -----------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------
# Custom Logger (Locust-safe)
# -----------------------------
logger = logging.getLogger("system_settings_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(
        "performanceTest/03__SystemSettings/TerminalOutput/logsource.log",
        mode="a"
    )
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s | %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

logger.propagate = False


class GetSystemSettingsUser(HttpUser):
    wait_time = constant(0)

    # ----- Global counters -----
    max_requests = 250
    request_count = 0
    user_count = 0
    lock = threading.Lock()

    def on_start(self):
        with GetSystemSettingsUser.lock:
            GetSystemSettingsUser.user_count += 1
            self.user_number = GetSystemSettingsUser.user_count

    @task
    def get_system_settings(self):

        with GetSystemSettingsUser.lock:
            if GetSystemSettingsUser.request_count >= GetSystemSettingsUser.max_requests:
                raise StopUser()

            GetSystemSettingsUser.request_count += 1
            current_request = GetSystemSettingsUser.request_count

        headers = {
            "accept": "application/json",
            "Authorization": read_token
        }

        with self.client.get(
            "/api/v1/system-settings",
            headers=headers,
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

#locust -f performanceTest/03__SystemSettings/ViewGeneral_user.py --host=https://10.45.12.32