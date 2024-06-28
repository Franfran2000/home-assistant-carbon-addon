from requests import get, post
from requests import auth
import os
import random
import time

from datetime import datetime

class BearerAuth(auth.AuthBase):
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

token = os.getenv('SUPERVISOR_TOKEN')
url = "http://supervisor/core/api/states"
headers = {
    "content-type": "application/json"
}

time_string = datetime.now().isoformat()

token_grid_map = "TOKEN"
headers = {
    "auth": token_grid_map
}
electricity_carbon = get("https://api.electricitymap.org/v3/carbon-intensity/history?zone=BE", headers=headers)
print(electricity_carbon.text)
elec_json = electricity_carbon.json()["history"]

total = 0
for d in elec_json:
    total += d["carbonIntensity"]
total /= len(elec_json)

current = elec_json[-1]["carbonIntensity"]
if total > current :
    s = "Now is a good time to use electricity"
else:
    s = "Now is not a good time to use electricity"

post_data = {
    "state": f"{s}",
    "attributes": {
        "time": time_string
    }
}

post_url = "http://supervisor/core/api/states/carbon.carbon_use"
post_headers = {
    "content-type": "application/json"
}
headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
post_response = post(post_url, headers=headers, json=post_data)

post_data = {
    "state": f"Average CO2 intensity: {total:.2f}",
    "attributes": {
        "unit_of_measurement": "gCO2eq/kWh",
        "time": time_string
    }
}

post_url = "http://supervisor/core/api/states/carbon.average_carbon_use"
post_headers = {
    "content-type": "application/json"
}
headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
post_response = post(post_url, headers=headers, json=post_data)

post_data = {
    "state": f"Current CO2 intensity: {current}",
    "attributes": {
        "unit_of_measurement": "gCO2eq/kWh",
        "time": time_string
    }
}

post_url = "http://supervisor/core/api/states/carbon.current_carbon_use"
post_headers = {
    "content-type": "application/json"
}
headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
post_response = post(post_url, headers=headers, json=post_data)

while True:

    time_string2 = datetime.now().isoformat()
    response = get(url, headers=headers, auth=BearerAuth(token))
    #print(response.text)
    j = response.json()

    device_types = {"light": 2.55, "sensor": 3.99, "binary_sensor": 3.99, "switch": 1.81}
    # values estimated using the framework
    devices = []
    names = set()
    for dic in j:

        entity_id = dic.get("entity_id", "").split('.')
        name_id = entity_id[1].split('_')
        if entity_id[0].lower() in device_types.keys() and dic.get("state", "") != "unavailable":
            if (entity_id[0],name_id[0]) not in names:
                names.add((entity_id[0],name_id[0]))
                devices += [entity_id[0].lower()]

    sum_carbon = 0
    for device in devices:
        sum_carbon += device_types[device]

    post_data = {
        "state": f"{sum_carbon:.2f}",
        "attributes": {
            "unit_of_measurement": "kgCO2-eq",
            "time":time_string2
        }
    }

    post_url = "http://supervisor/core/api/states/carbon.carbon_emitted"
    post_headers = {
        "content-type": "application/json"
    }
    headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
    post_response = post(post_url, headers=headers, json=post_data)
    #print(post_response.text)sd  

    time.sleep(5)
