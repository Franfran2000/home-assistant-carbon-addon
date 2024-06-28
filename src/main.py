from requests import get, post
from requests import auth
import os
import random
import time

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

while True:
    response = get(url, headers=headers, auth=BearerAuth(token))
    #print(response.text)
    j = response.json()
    # values estimated using the framework

    devices = []
    names = set()
    for dic in j:
        #print(dic)
        #print(dic.get("entity_id", ""))
        entity_id = dic.get("entity_id", "").split('.')
        name_id = entity_id[1].split('_')
        if entity_id[0].lower() in device_types.keys() and dic.get("state", "") != "unavailable":
            if (entity_id[0],name_id[0]) not in names:
                names.add((entity_id[0],name_id[0]))
                devices += [entity_id[0].lower()]
    #print(devices)

    sum_carbon = 0
    for device in devices:
        sum_carbon += device_types[device]

    # for i in range(100):
    #     sum_carbon += random.randint(1, 10)

    post_data = {
        "state": f"{sum_carbon:.2f}",
        "attributes": {
            "unit_of_measurement": "kgCO2-eq",
            "time":"2024-06-26T15:17:52+00:00"
        }
    }

    post_url = "http://supervisor/core/api/states/sensor.carbon_emitted"
    #local_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIxNzE5NzBmNDkxMjY0OGFlOWFhYmUyYTlmZDE1ZjkzYyIsImlhdCI6MTcxOTQwODMyOSwiZXhwIjoyMDM0NzY4MzI5fQ.n9yLPkBHEKD3sq41eZHkAiOh6xfrq3e_nXr_yuKhonM"
    post_headers = {
        "content-type": "application/json"
    }
    headers = {"Authorization": f"Bearer {token}", "content-type": "application/json"}
    post_response = post(post_url, headers=headers, json=post_data)
    #print(post_response.text)

    token_grid_map = "ixy73lHlChCgK"
    headers = {
        "zone": "Be",
        "auth": token_grid_map
    }
    electricity_carbon = get("https://api.electricitymap.org/v3/carbon-intensity/history", headers=headers)
    print(electricity_carbon.json())

    time.sleep(120)
