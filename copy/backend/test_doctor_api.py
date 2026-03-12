import requests

BASE = "http://127.0.0.1:8000/api"

# 1. GET /doctors
r = requests.get(f"{BASE}/doctors")
print(f"GET /doctors -> {r.status_code}")
docs = r.json()
print(f"  Count: {len(docs)}")
if docs:
    d = docs[0]
    print(f"  Fields: {list(d.keys())}")
    print(f"  specialization: {d.get('specialization')}")
    print(f"  experience: {d.get('experience')}")
    print(f"  consultation_fee: {d.get('consultation_fee')}")
    print(f"  password exposed: {'password' in d}")

    # 2. GET /doctor/{id} - valid
    doc_id = d["_id"]
    r2 = requests.get(f"{BASE}/doctor/{doc_id}")
    print(f"\nGET /doctor/{{valid_id}} -> {r2.status_code}")

    # 3. GET /doctor/{id} - not found (valid format, no match)
    r3 = requests.get(f"{BASE}/doctor/000000000000000000000000")
    print(f"GET /doctor/000000000000000000000000 -> {r3.status_code}: {r3.json()}")

    # 4. GET /doctor/{id} - bad format
    r4 = requests.get(f"{BASE}/doctor/bad-id")
    print(f"GET /doctor/bad-id -> {r4.status_code}: {r4.json()}")

    # 5. Filter by specialization
    spec = d.get("specialization", "Cardiology")
    r5 = requests.get(f"{BASE}/doctors", params={"specialization": spec})
    print(f"\nGET /doctors?specialization={spec} -> {r5.status_code}, count: {len(r5.json())}")
