from locust import HttpUser, task, between
import random
import string

class AddBookUser(HttpUser):
    wait_time = between(1, 2)
    host = "https://rahulshettyacademy.com"  # Add this line

    @task
    def add_book(self):
        isbn = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        aisle = str(random.randint(100, 999))
        
        payload = {
            "name": "Learn Appium Automation with Java",
            "isbn": isbn,
            "aisle": aisle,
            "author": "John foe"
        }

        headers = {"Content-Type": "application/json"}
        response = self.client.post("/Library/Addbook.php", json=payload, headers=headers)

        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Failed with status code: {response.status_code}")
