import requests
import os

ACCESS_TOKEN = os.getenv('ACCESS_TOKEN', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzYxNjI3NTA0LCJpYXQiOjE3NjE2MjM5MDQsImp0aSI6ImU3MjY4NDI3NDVkNDQzZjhhZjk2NzZjMzExZTNlYjNiIiwidXNlcl9pZCI6IjYifQ.42s4djbFiqjFqFtj8q6viIMqrhlxWwMfEElLTHbNHgo')
BASE_URL = os.getenv('BASE_URL', 'http://127.0.0.1:8000/api')

url = f"{BASE_URL}/operations/available-doctors/?department=general-medicine"
headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}

try:
    resp = requests.get(url, headers=headers, timeout=5)
    print('Status:', resp.status_code)
    print('Body:', resp.text[:800])
except Exception as e:
    print('Error:', e)