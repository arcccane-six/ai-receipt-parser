import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()


def chat(messages, model=None, json_mode=True):
    payload = {"model": model or os.environ["LLM_MODEL"], "messages": messages}
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    r = requests.post(
        f"{os.environ['LLM_BASE_URL']}/chat/completions",
        headers={"Authorization": f"Bearer {os.environ['LLM_API_KEY']}"},
        json=payload,
    )
    if r.status_code != 200:
        print(f"Gagal: {r.status_code} - {r.text}")
        raise SystemExit(1)
    return r.json()["choices"][0]["message"]["content"]


SYSTEM = (
    "Kamu ekstraktor data transaksi. Ubah teks jadi JSON dengan format "
    '{"items": [{"nama": string, "qty": number|null, "harga": number|null}], '
    '"total": number|null, "payment": string|null}. '
    "ATURAN: ambil hanya yang tertulis. Kalau tidak ada, isi null. "
    "JANGAN menebak. Balas JSON saja."
)

teks = "kopi susu 2 gelas 10rb, es teh 1 5rb, total 25rb, bayar qris"

content = chat([
    {"role": "system", "content": SYSTEM},
    {"role": "user", "content": teks},
])

data = json.loads(content)

sum_ = sum((i.get("qty") or 0) * (i.get("harga") or 0) for i in data.get("items") or [])
data["valid"] = None if data.get("total") is None else sum_ == data["total"]

print(json.dumps(data, indent=2, ensure_ascii=False))