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
logger = logging.getLogger("put_mode_of_operation_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(
        "performanceTest/03__SystemSettings/TerminalOutput/put_mode_of_operation.log",
        mode="a"
    )
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s | %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

logger.propagate = False


class PutModeOfOperationUser(HttpUser):
    wait_time = constant(0)

    # ----- Global counters -----
    max_requests = 500
    request_count = 0
    user_count = 0
    lock = threading.Lock()

    def on_start(self):
        with PutModeOfOperationUser.lock:
            PutModeOfOperationUser.user_count += 1
            self.user_number = PutModeOfOperationUser.user_count

    @task
    def put_mode_of_operation(self):
        with PutModeOfOperationUser.lock:
            if PutModeOfOperationUser.request_count >= PutModeOfOperationUser.max_requests:
                raise StopUser()

            PutModeOfOperationUser.request_count += 1
            current_request = PutModeOfOperationUser.request_count

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": write_token  # Should already contain "Bearer <token>"
        }

        payload = {
            "mode_of_operation": "distributed_collector",        #'distributed_collector', 'syslog_forwarder', 'normal'
            "is_buffering_enabled": False
        }

        with self.client.put(
            "/api/v1/system-settings/mode-of-operation",
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

#locust -f performanceTest/03__SystemSettings/ModeOfOperation.py --host=https://10.45.12.33