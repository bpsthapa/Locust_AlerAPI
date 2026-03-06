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
logger = logging.getLogger("syslog_collector_logger")
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


class GetSyslogCollectorUser(HttpUser):
    wait_time = constant(0)

    # ----- Global counters -----
    max_requests = 500
    request_count = 0
    user_count = 0
    lock = threading.Lock()

    def on_start(self):
        with GetSyslogCollectorUser.lock:
            GetSyslogCollectorUser.user_count += 1
            self.user_number = GetSyslogCollectorUser.user_count

    @task
    def get_syslog_collector(self):

        with GetSyslogCollectorUser.lock:
            if GetSyslogCollectorUser.request_count >= GetSyslogCollectorUser.max_requests:
                raise StopUser()

            GetSyslogCollectorUser.request_count += 1
            current_request = GetSyslogCollectorUser.request_count

        headers = {
            "accept": "application/json",
            "Authorization": write_token   # should already be "Bearer
        }

        with self.client.get(
            "/api/v1/syslog-collector/69a01457d745893da97b4304",
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


#locust -f performanceTest/LogSource/ViewSyslogCollector.py --host=https://10.45.12.32