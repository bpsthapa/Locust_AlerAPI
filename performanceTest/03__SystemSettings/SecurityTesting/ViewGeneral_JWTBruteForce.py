from locust import HttpUser, task, constant
import threading
import logging
from performanceTest.TestData.ConfigAPI_78 import *

# ---------- Token Configuration ----------
TOKEN_PREFIX = "Bearer 124afda"
TOKEN_START_NUMBER = 1231  # starting number

# ---------- Custom Logger (Locust-safe) ----------
logger = logging.getLogger("system_settings_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(
    "performanceTest/03__SystemSettings/TerminalOutput/system_settings.log", mode="a"
)
stream_handler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s | %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

# Prevent Locust from overriding this logger
logger.propagate = False


class GetSystemSettingsUser(HttpUser):
    wait_time = constant(0)

    # ----- Global counters -----
    max_requests = 10000
    request_count = 0
    user_count = 0
    lock = threading.Lock()

    def on_start(self):
        # Assign unique user number
        with GetSystemSettingsUser.lock:
            GetSystemSettingsUser.user_count += 1
            self.user_number = GetSystemSettingsUser.user_count

    @task
    def get_system_settings(self):
        with GetSystemSettingsUser.lock:
            # Stop test after max_requests
            if GetSystemSettingsUser.request_count >= GetSystemSettingsUser.max_requests:
                for handler in logger.handlers:
                    handler.flush()
                self.environment.runner.quit()
                return

            GetSystemSettingsUser.request_count += 1
            current_request = GetSystemSettingsUser.request_count

            # 🔑 Increment token number per request
            token_number = TOKEN_START_NUMBER + current_request - 1
            token = f"{TOKEN_PREFIX}{token_number}"

        headers = {
            "accept": "application/json",
            "Authorization": token
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
                    f"TOKEN: {token} | "
                    f"FAILED | Status: {response.status_code}"
                )
                logger.error(msg)
                response.failure(msg)
            else:
                msg = (
                    f"User #{self.user_number} | "
                    f"Request #{current_request} | "
                    f"TOKEN: {token} | "
                    f"SUCCESS | Status: {response.status_code}"
                )
                logger.info(msg)
                response.success()

#locust -f performanceTest/03__SystemSettings/SecurityTesting/ViewGeneral_JWTBruteForce.py --host=https://10.45.12.33