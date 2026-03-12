import requests, json

r = requests.get("http://127.0.0.1:8000/openapi.json")
paths = r.json()["paths"]
for path in sorted(paths.keys()):
    methods = [m.upper() for m in paths[path].keys()]
    print(f"{str(methods):<20} {path}")
