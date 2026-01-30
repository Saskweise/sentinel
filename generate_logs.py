import requests
from datetime import datetime
from log import Log

URL = "http://localhost:8000/logs"

def send_log(ip, route, execution_code):
    new_log = Log(
            ip = ip,
            request = "POST",
            route = route,
            timestamp = datetime.now().isoformat(),
            code_response = execution_code
            )
    requests.post(URL, data=new_log.model_dump_json()) # Convierte el new_log en json
    print(f"Log sent: {ip} -> {route}")


for i in range(20):
    send_log("192.168.1.104", "/api/data", 200)
 
for i in range(15):
    send_log("203.0.113.45", "/admin", 403)