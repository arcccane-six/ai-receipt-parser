import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
URL = os.environ["WEBHOOK_URL"]

tests = [
    "kopi susu 2 gelas, es teh 1, total 50rb, bayar QRIS",
    "beli bakso 15k sama es campur, lupa bayar berapa, pokoknya qris",
    "kjashdkashd",
    "iem 700rb, dac iem 1jt, eartips 70rb",
]

hasil = []
for i, teks in enumerate(tests, 1):
    r = requests.post(URL, json={"teks": teks})
    hasil.append({"test": i, "input": teks, "status": r.status_code, "output": r.json()})
    print(f"Test {i}: status {r.status_code}")

with open("results.json", "w") as f:
    json.dump(hasil, f, indent=2, ensure_ascii=False)
print("Selesai — results.json tersimpan")