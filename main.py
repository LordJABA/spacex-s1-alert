import requests
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Query SEC EDGAR directly by SpaceX CIK — zero false positives
SEC_URL = (
    "https://data.sec.gov/submissions/CIK0001181412.json"
)

HEADERS = {
    "User-Agent": "SpaceX-S1-Monitor contact@youremail.com"
}

def send_telegram(message):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("ERROR: Telegram credentials missing from environment.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    r = requests.post(url, json=payload)
    print(f"Telegram status: {r.status_code} | Response: {r.text}")

def check_sec():
    print("Checking SEC EDGAR via CIK direct lookup...")
    response = requests.get(SEC_URL, headers=HEADERS, timeout=10)
    data = response.json()

    filings = data.get("filings", {}).get("recent", {})
    forms = filings.get("form", [])
    dates = filings.get("filingDate", [])
    accession = filings.get("accessionNumber", [])

    # Look for S-1 or S-1/A in recent filings
    found = []
    for i, form in enumerate(forms):
        if form in ("S-1", "S-1/A"):
            found.append({
                "form": form,
                "date": dates[i],
                "accession": accession[i].replace("-", "")
            })

    print(f"S-1 filings found for SpaceX CIK: {len(found)}")

    if found:
        f = found[0]
        link = f"https://www.sec.gov/Archives/edgar/data/1181412/{f['accession']}/"
        msg = (
            f"🚨🚨🚨 *SPACEX S-1 FILED* 🚨🚨🚨\n\n"
            f"*Form:* {f['form']}\n"
            f"*Filed:* {f['date']}\n\n"
            f"*READ IT NOW:*\n{link}"
        )
        send_telegram(msg)
        print("ALERT SENT.")
    else:
        print("No S-1 found. All clear.")

if __name__ == "__main__":
    check_sec()
