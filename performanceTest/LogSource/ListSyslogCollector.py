from locust import HttpUser, task, constant
import threading
import logging
import os
from performanceTest.TestData.ConfigAPI_78 import *

# ---------- Log file in SAME directory as this script ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(BASE_DIR, "output.log")

# ---------- Custom Logger (Locust-safe) ----------
logger = logging.getLogger("syslog_collector_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_path, mode="a")
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
    max_requests = 1000
    request_count = 0
    user_count = 0
    lock = threading.Lock()

    def on_start(self):
        with GetSyslogCollectorUser.lock:
            GetSyslogCollectorUser.user_count += 1
            self.user_number = GetSyslogCollectorUser.user_count

    @task
    def get_syslog_collectors(self):

        # ----- Stop test after max_requests -----
        with GetSyslogCollectorUser.lock:
            if GetSyslogCollectorUser.request_count >= GetSyslogCollectorUser.max_requests:
                for handler in logger.handlers:
                    handler.flush()
                self.environment.runner.quit()
                return

            GetSyslogCollectorUser.request_count += 1
            current_request = GetSyslogCollectorUser.request_count

        headers = {
            "accept": "application/json",
            "Authorization": read_token   # should already be "Bearer xxx"
        }

        params = {
            "limit": 10,
            "sort_order": "desc",
            "sort_by": "name"
        }

        with self.client.get(
            "/api/v1/syslog-collector",
            headers=headers,
            params=params,
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


#locust -f performanceTest/LogSource/ListSyslogCollector.py --host=https://10.45.12.33