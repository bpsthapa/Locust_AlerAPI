from locust import HttpUser, task, constant
from locust.exception import StopUser
import threading
import logging
import urllib3
import random

from performanceTest.TestData.ConfigAPI_78 import *

# -----------------------------
# Disable SSL Warning (internal env only)
# -----------------------------
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------
# Custom Logger
# -----------------------------
logger = logging.getLogger("create_syslog_collector_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(
        "performanceTest/03__SystemSettings/TerminalOutput/create_syslog_collector.log",
        mode="a"
    )
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s | %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

logger.propagate = False


class CreateSyslogCollectorUser(HttpUser):
    wait_time = constant(0)

    # ----- Global Counters -----
    max_requests = 5
    request_count = 0
    user_count = 0
    lock = threading.Lock()

    def on_start(self):
        with CreateSyslogCollectorUser.lock:
            CreateSyslogCollectorUser.user_count += 1
            self.user_number = CreateSyslogCollectorUser.user_count

    @task
    def create_syslog_collector(self):

        with CreateSyslogCollectorUser.lock:
            if CreateSyslogCollectorUser.request_count >= CreateSyslogCollectorUser.max_requests:
                raise StopUser()

            CreateSyslogCollectorUser.request_count += 1
            current_request = CreateSyslogCollectorUser.request_count

        # ---- Generate Unique Name ----
        unique_name = f"LogSource_{current_request}_{random.randint(1000,9999)}"

        # ---- Generate Unique IP Address ----
        unique_ip = f"10.45.{random.randint(1,254)}.{random.randint(1,254)}"

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": write_token  # must contain "Bearer <token>"
        }

        payload = {
            "config": {
                "RoutingPolicy": {
                    "routing_criterion": [],
                    "catch_all": "default"
                },
                "NormalizationPolicy": {},
                "Source": {
                    "name": unique_name,
                    "timezone": "UTC",
                    "addresses": [unique_ip],
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

            if response.status_code not in [200, 201]:
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
                    f"SUCCESS | Created: {unique_name} | IP: {unique_ip}"
                )
                logger.info(msg)
                response.success()

#locust -f performanceTest/LogSource/CreateSyslog.py --host=https://10.45.12.32