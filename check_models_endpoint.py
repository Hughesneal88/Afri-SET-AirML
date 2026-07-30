import urllib.request
import json

res = urllib.request.urlopen('http://127.0.0.1:5000/api/models')
data = json.loads(res.read().decode())
print("Status:", data["status"])
print(f"Registered Models Count: {len(data['models'])}\n")

for k, m in data["models"].items():
    print(f" • Key: {k:35s} | Features: {m['features']:2d} | Name: {m['name']}")
