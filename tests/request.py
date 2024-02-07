#!/usr/bin/env python3
import requests
from json import dumps


group_names = ["Role: Engineering Manager"]
profile = {
    "phiaccess": True,
    "countryCode": "US",
    "userType": "EMPLOYEE",
    "jobprofile": "HealthCoachPremium",
    "pm": "Y",
}

data = {"group_names": group_names, "profile": profile}

res = requests.post("http://localhost:8000/graph", json=data)
try:
    print(dumps(res.json()))
except Exception:
    print(res.status_code)
