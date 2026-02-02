import requests
from datetime import datetime
from log import Log

URL = "http://localhost:8000/logs"

# A session is opened, so multiple queries can be sent
session = requests.Session()

def send_log(ip, route, execution_code):
    new_log = Log(
            ip = ip,
            request = "POST",
            route = route,
            timestamp = datetime.now().isoformat(),
            code_response = execution_code
            )
    
    try:
        session.post(URL, data=new_log.model_dump_json(), timeout=1) # Converts new_log into json 
        print(f"Log sent: {ip} -> {route}")
    except Exception as e:
        print(f"Error: {e}")

def send_log_fast(ip, route, execution_code):
    new_log = Log(
            ip = ip,
            request = "POST",
            route = route,
            timestamp = datetime.now().isoformat(),
            code_response = execution_code
            )
    
    try:
        session.post(URL, data=new_log.model_dump_json(), timeout=0.2) # Converts new_log into json 
        print(f"Log sent: {ip} -> {route}")
    except Exception as e:
        print(f"Error: {e}")


for i in range(100):
    send_log("192.168.1.104", "/api/data", 200)
    send_log("192.168.1.257", "/api/data", 200)
    send_log("192.168.1.108", "/api/data", 200)
    send_log("192.168.1.257", "/status", 200)
    send_log("192.168.1.104", "/admin", 403)
    send_log("192.168.1.257", "/analyze", 403)
    send_log_fast("192.168.1.3", "/status", 200)
    send_log_fast("192.168.1.132", "/status", 200)
    send_log_fast("192.168.1.100", "/status", 200)

for i in range(25):
    send_log_fast("203.0.113.45", "/admin", 403)
    send_log_fast("203.0.113.45", "/status", 200)
    send_log_fast("223.1.299.34", "/admin", 403)
    send_log_fast("333.0.132.76", "/admin", 403)
    