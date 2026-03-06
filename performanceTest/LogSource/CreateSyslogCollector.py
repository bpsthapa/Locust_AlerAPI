from locust import HttpUser, task, constant
from locust.exception import StopUser
import threading
import logging
import os
from performanceTest.TestData.ConfigAPI_78 import *

# ---------- Log file in SAME directory ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(BASE_DIR, "output.log")

# ---------- Logger ----------
logger = logging.getLogger("syslog_create_logger")
logger.setLevel(logging.INFO)

file_handler = logging.FileHandler(log_path, mode="a")
stream_handler = logging.StreamHandler()

formatter = logging.Formatter("%(asctime)s | %(message)s")
file_handler.setFormatter(formatter)
stream_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.propagate = False


class CreateSyslogCollectorUser(HttpUser):
    wait_time = constant(0)

    # ----- Counters -----
    max_requests = 1000
    request_count = 0
    user_count = 0
    lock = threading.Lock()

    def on_start(self):
        with CreateSyslogCollectorUser.lock:
            CreateSyslogCollectorUser.user_count += 1
            self.user_number = CreateSyslogCollectorUser.user_count

    @task
    def create_syslog_collector(self):

        # ----- Stop Condition (Clean Stop) -----
        with CreateSyslogCollectorUser.lock:
            if CreateSyslogCollectorUser.request_count >= CreateSyslogCollectorUser.max_requests:
                for handler in logger.handlers:
                    handler.flush()
                raise StopUser()

            CreateSyslogCollectorUser.request_count += 1
            current_request = CreateSyslogCollectorUser.request_count

        # ----- Dynamic Values -----
        dynamic_name = f"LogSourceName_{current_request}"
        dynamic_ip = f"10.45.2.{(current_request % 250) + 1}"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": write_token   # must include Bearer
        }

        payload = {
            "config": {
                "RoutingPolicy": {
                    "routing_criterion": [],
                    "catch_all": "default"
                },
                "NormalizationPolicy": {},
                "Source": {
                    "name": dynamic_name,
                    "timezone": "UTC",
                    "addresses": [dynamic_ip],
                    "confidentiality": "Minimal",
                    "integrity": "Minimal",
                    "availability": "Minimal"
                },
                "Connector": {
                    "charset": "utf_8",
                    "parser": "SyslogParser"
                }
            }
        }

        with self.client.post(
            "/api/v1/syslog-collector",
            headers=headers,
            json=payload,
            verify=False,
            catch_response=True
        ) as response:

            if response.status_code not in (200, 201):
                msg = (
                    f"User #{self.user_number} | "
                    f"Request #{current_request} | "
                    f"FAILED | Status: {response.status_code} | "
                    f"Name: {dynamic_name} | IP: {dynamic_ip}"
                )
                logger.error(msg)
                response.failure(msg)
            else:
                msg = (
                    f"User #{self.user_number} | "
                    f"Request #{current_request} | "
                    f"SUCCESS | Status: {response.status_code} | "
                    f"Name: {dynamic_name} | IP: {dynamic_ip}"
                )
                logger.info(msg)
                response.success()


#locust -f performanceTest/LogSource/CreateSyslogCollector.py --host=https://10.45.12.32