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
logger = logging.getLogger("update_syslog_collector_logger")
logger.setLevel(logging.INFO)

if not logger.handlers:
    file_handler = logging.FileHandler(
        "performanceTest/03__SystemSettings/TerminalOutput/update_syslog_collector.log",
        mode="a"
    )
    stream_handler = logging.StreamHandler()

    formatter = logging.Formatter("%(asctime)s | %(message)s")
    file_handler.setFormatter(formatter)
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

logger.propagate = False


class UpdateSyslogCollectorUser(HttpUser):
    wait_time = constant(0)

    # ----- Global Counters -----
    max_requests = 1500
    request_count = 0
    user_count = 0
    lock = threading.Lock()

    collector_id = "69a7fbc5218f0816fcec4ec2"  # ID to update

    def on_start(self):
        with UpdateSyslogCollectorUser.lock:
            UpdateSyslogCollectorUser.user_count += 1
            self.user_number = UpdateSyslogCollectorUser.user_count

    @task
    def update_syslog_collector(self):

        with UpdateSyslogCollectorUser.lock:
            if UpdateSyslogCollectorUser.request_count >= UpdateSyslogCollectorUser.max_requests:
                raise StopUser()

            UpdateSyslogCollectorUser.request_count += 1
            current_request = UpdateSyslogCollectorUser.request_count

        # ---- Unique Source Name ----
        unique_name = f"500LogSource_{self.user_number}_{current_request}"

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
                "NormalizationPolicy": {
                    "normalizers": [
                        {"name": "BlueCoatnFMAINNormalizer", "type": "compiled"}
                    ]
                },
                "EnrichmentPolicy": "667a7dc13acc961eed116fd9",
                "Source": {
                    "name": unique_name,
                    "timezone": "UTC",
                    "addresses": [f"2.3.{random.randint(1,254)}.{random.randint(1,254)}"],
                    "confidentiality": "Minimal",
                    "integrity": "Minimal",
                    "availability": "Minimal",
                    "device_groups": ["linux"],
                    "inactivity_threshold_minutes": 70
                },
                "Connector": {
                    "charset": "utf_8",
                    "parser": "SyslogParser"
                }
            }
        }

        with self.client.put(
            f"/api/v1/syslog-collector/{self.collector_id}",
            headers=headers,
            json=payload,
            verify=False,
            catch_response=True
        ) as response:

            if response.status_code not in [200, 204]:
                msg = (
                    f"User #{self.user_number} | "
                    f"Request #{current_request} | "
                    f"FAILED | Status: {response.status_code} | "
                    f"Response: {response.text} | Name: {unique_name}"
                )
                logger.error(msg)
                print(msg)
                response.failure(msg)

            else:
                msg = (
                    f"User #{self.user_number} | "
                    f"Request #{current_request} | "
                    f"SUCCESS | Updated: {unique_name} | IP: {payload['config']['Source']['addresses'][0]}"
                )
                logger.info(msg)
                print(msg)
                response.success()

#locust -f performanceTest/LogSource/UpdateLogSource.py --host=https://10.45.12.32