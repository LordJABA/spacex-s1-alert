import requests
import time
import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

SEC_URL = (
    "https://efts.sec.gov/LATEST/search-index?"
    "q=%22Space+Exploration+Technologies%22"
    "&forms=S-1"
    "&dateRange=custom"
    "&startdt=2026-01-01"
)

HEADERS = {
    "User-Agent": "SpaceX-S1-Monitor contact@youremail.com"
}

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    requests.post(url, json=payload)

def check_sec():
    try:
        response = requests.get(SEC_URL, headers=HEADERS, timeout=10)
        data = response.json()
        hits = data.get("hits", {}).get("hits", [])
        if len(hits) > 0:
            filing = hits[0]["_source"]
            entity = filing.get("entity_name", "Unknown")
            form = filing.get("form_type", "Unknown")
            filed = filing.get("file_date", "Unknown")
            link = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001181412&type=S-1&dateb=&owner=include&count=40"
            msg = (
                f"🚨🚨🚨 *SPACEX S-1 FILED* 🚨🚨🚨\n\n"
                f"*Entity:* {entity}\n"
                f"*Form:* {form}\n"
                f"*Filed:* {filed}\n\n"
                f"*READ IT NOW:*\n{link}"
            )
            send_telegram(msg)
            return True
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    send_telegram("🚀 *SpaceX S1 Monitor is LIVE* — watching SEC EDGAR every 60 seconds.")
    print("Monitor started. Watching SEC EDGAR...")
    
    already_alerted = False
    
    while True:
        if not already_alerted:
            found = check_sec()
            if found:
                already_alerted = True
                print("S-1 DETECTED. Alert sent. Stopping checks.")
        time.sleep(60)

if __name__ == "__main__":
    main()
