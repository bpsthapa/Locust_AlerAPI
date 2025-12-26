from locust import HttpUser, task, constant, between
import threading
import webbrowser

from performanceTest.TestData.ConfigAPI_78 import *

class GetSystemSettingsUser(HttpUser):
    wait_time = constant(0)  # no delay between requests
    #wait_time = between(1, 2)

    max_requests = 100
    request_count = 0
    lock = threading.Lock()
    user_count = 0

    @task
    def get_system_settings(self):
        # Stop test after max_requests
        with GetSystemSettingsUser.lock:
            if GetSystemSettingsUser.request_count >= GetSystemSettingsUser.max_requests:
                self.environment.runner.quit()
                return
            GetSystemSettingsUser.request_count += 1

        headers = {
            "accept": "application/json",
            "Authorization": read_token
        }

        with self.client.get(
            "/api/v1/system-settings",
            headers=headers,
            verify=False,  # skip SSL verification if needed
            catch_response=True
        ) as response:
            if response.status_code != 200:
                print(f"Request #{GetSystemSettingsUser.request_count} -> Failed Status Code: {response.status_code}")
                response.failure(f"Failed with status {response.status_code}: {response.text}")
            else:
                response.success()
                #print(f"Request #{GetSystemSettingsUser.request_count} -> response is {response.text}")
                print(f"Request #{GetSystemSettingsUser.request_count} -> Status Code: {response.status_code}")


webbrowser.get('open -a /Applications/Google\ Chrome.app %s').open('http://0.0.0.0:8089')

#locust -f performanceTest/03__SystemSettings/ViewGeneral.py --host=https://10.45.3.78