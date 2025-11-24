import time
import requests
import re
import json
from pathlib import Path

TELEGRAM_BOT_TOKEN = "8433073477:AAGjne_lOu5cSqpGulLTXEBp81HT1RZ-_5Q"
CHAT_ID = 704487153
CHECK_INTERVAL = 15 * 60

FILTER_URLS = [
    "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Year.range(202300..)._.Hidden.N._.MultiView2Hidden.N._.(C.CarType.Y._.(C.Manufacturer.%EA%B8%B0%EC%95%84._.(C.ModelGroup.%EC%8F%98%EB%A0%8C%ED%86%A0._.(C.Model.%EC%8F%98%EB%A0%8C%ED%86%A0%204%EC%84%B8%EB%8C%80._.(C.BadgeGroup.%EA%B0%80%EC%86%94%EB%A6%B0%2B%EC%A0%84%EA%B8%B0%201600cc._.(Or.Badge.HEV%201_.6%204WD._.Badge.HEV%201_.6%202WD.))))))_.SellType.%EC%9D%BC%EB%B0%98.)%22%2C%22title%22%3A%22%EA%B8%B0%EC%95%84%20%EC%8F%98%EB%A0%8C%ED%86%A0%204%EC%84%B8%EB%8C%80(20~23%EB%85%84)%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobilePriceAsc%22%7D",
    "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Year.range(202300..)._.Hidden.N._.MultiView2Hidden.N._.(C.CarType.Y._.(C.Manufacturer.%EA%B8%B0%EC%95%84._.(C.ModelGroup.%EC%8F%98%EB%A0%8C%ED%86%A0._.(C.Model.%EC%8F%98%EB%A0%8C%ED%86%A0%204%EC%84%B8%EB%8C%80._.(C.BadgeGroup.%EA%B0%80%EC%86%94%EB%A6%B0%2B%EC%A0%84%EA%B8%B0%201600cc._.(Or.Badge.HEV%201_.6%204WD._.Badge.HEV%201_.6%202WD.))))))_.SellType.%EC%9D%BC%EB%B0%98.)%22%2C%22title%22%3A%22%EA%B8%B0%EC%95%84%20%EC%8F%98%EB%A0%8C%ED%86%A0%204%EC%84%B8%EB%8C%80(20~23%EB%85%84)%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobilePriceAsc%22%7D",
    "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Hidden.N._.MultiView2Hidden.N._.Year.range(202300..)._.Hidden.N._.SellType.%EC%9D%BC%EB%B0%98._.(C.CarType.Y._.(C.Manufacturer.%EA%B8%B0%EC%95%84._.(C.ModelGroup.%EC%8F%98%EB%A0%8C%ED%86%A0._.(C.Model.%EB%8D%94%20%EB%89%B4%20%EC%8F%98%EB%A0%8C%ED%86%A0%204%EC%84%B8%EB%8C%80._.BadgeGroup.%EA%B0%80%EC%86%94%EB%A6%B0%2B%EC%A0%84%EA%B8%B0%201600cc.)))))%22%2C%22title%22%3A%22%EA%B8%B0%EC%95%84%20%EB%8D%94%20%EB%89%B4%20%EC%8F%98%EB%A0%8C%ED%86%A0%204%EC%84%B8%EB%8C%80(23%EB%85%84~%ED%98%84%EC%9E%AC)%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobileModifiedDate%22%7D",
    "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Hidden.N._.MultiView2Hidden.N._.Year.range(202300..)._.Hidden.N._.SellType.%EC%9D%BC%EB%B0%98._.(C.CarType.Y._.(C.Manufacturer.%EA%B8%B0%EC%95%84._.(C.ModelGroup.%EC%8A%A4%ED%8F%AC%ED%8B%B0%EC%A7%80._.(C.Model.%EC%8A%A4%ED%8F%AC%ED%8B%B0%EC%A7%80%205%EC%84%B8%EB%8C%80._.(Or.BadgeGroup.%EA%B0%80%EC%86%94%EB%A6%B0%202WD._.BadgeGroup.%EA%B0%80%EC%86%94%EB%A6%B0%204WD.))))))%22%2C%22title%22%3A%22%EA%B8%B0%EC%95%84%20%EC%8A%A4%ED%8F%AC%ED%8B%B0%EC%A7%80%205%EC%84%B8%EB%8C%80(21%EB%85%84~%ED%98%84%EC%9E%AC)%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobileModifiedDate%22%7D",
    "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Hidden.N._.MultiView2Hidden.N._.Year.range(202300..)._.Hidden.N._.SellType.%EC%9D%BC%EB%B0%98._.(C.CarType.Y._.(C.Manufacturer.%EA%B8%B0%EC%95%84._.(C.ModelGroup.%EB%8B%88%EB%A1%9C._.(C.Model.%EB%94%94%20%EC%98%AC%20%EB%89%B4%20%EB%8B%88%EB%A1%9C._.BadgeGroup.%EA%B0%80%EC%86%94%EB%A6%B0%2B%EC%A0%84%EA%B8%B0%201600cc.)))))%22%2C%22title%22%3A%22%EA%B8%B0%EC%95%84%20%EB%94%94%20%EC%98%AC%20%EB%89%B4%20%EB%8B%88%EB%A1%9C(22%EB%85%84~%ED%98%84%EC%9E%AC)%22%2C%22toggle%22%3A%7B%22modelGroup%22%3A1%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobileModifiedDate%22%7D",
    "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Hidden.N._.MultiView2Hidden.N._.Year.range(202300..)._.Hidden.N._.SellType.%EC%9D%BC%EB%B0%98._.(C.CarType.Y._.(C.Manufacturer.%ED%98%84%EB%8C%80._.(C.ModelGroup.%ED%8C%B0%EB%A6%AC%EC%84%B8%EC%9D%B4%EB%93%9C._.Model.%EB%8D%94%20%EB%89%B4%20%ED%8C%B0%EB%A6%AC%EC%84%B8%EC%9D%B4%EB%93%9C.))))%22%2C%22title%22%3A%22%ED%98%84%EB%8C%80%20%EB%8D%94%20%EB%89%B4%20%ED%8C%B0%EB%A6%AC%EC%84%B8%EC%9D%B4%EB%93%9C(22~25%EB%85%84)%22%2C%22toggle%22%3A%7B%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobileModifiedDate%22%7D",
    "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Hidden.N._.MultiView2Hidden.N._.Year.range(202300..)._.Hidden.N._.SellType.%EC%9D%BC%EB%B0%98._.(C.CarType.Y._.(C.Manufacturer.%ED%98%84%EB%8C%80._.(C.ModelGroup.%ED%88%AC%EC%8B%BC._.(C.Model.%EB%8D%94%20%EB%89%B4%20%ED%88%AC%EC%8B%BC%20%ED%95%98%EC%9D%B4%EB%B8%8C%EB%A6%AC%EB%93%9C%20(NX4_)._.BadgeGroup.%EA%B0%80%EC%86%94%EB%A6%B0%2B%EC%A0%84%EA%B8%B0%201600cc.)))))%22%2C%22title%22%3A%22%ED%98%84%EB%8C%80%20%EB%8D%94%20%EB%89%B4%20%ED%88%AC%EC%8B%BC%20%ED%95%98%EC%9D%B4%EB%B8%8C%EB%A6%AC%EB%93%9C%20(NX4)(23%EB%85%84~%ED%98%84%EC%9E%AC)%22%2C%22toggle%22%3A%7B%22modelGroup%22%3A1%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobileModifiedDate%22%7D",
    "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Hidden.N._.MultiView2Hidden.N._.Year.range(202300..)._.Hidden.N._.SellType.%EC%9D%BC%EB%B0%98._.(C.CarType.Y._.(C.Manufacturer.%ED%98%84%EB%8C%80._.(C.ModelGroup.%ED%88%AC%EC%8B%BC._.Model.%ED%88%AC%EC%8B%BC%20%ED%95%98%EC%9D%B4%EB%B8%8C%EB%A6%AC%EB%93%9C%20(NX4_).))))%22%2C%22title%22%3A%22%ED%98%84%EB%8C%80%20%ED%88%AC%EC%8B%BC%20%ED%95%98%EC%9D%B4%EB%B8%8C%EB%A6%AC%EB%93%9C%20(NX4)(20~23%EB%85%84)%22%2C%22toggle%22%3A%7B%22modelGroup%22%3A1%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobileModifiedDate%22%7D",
    "https://car.encar.com/list/car?page=1&search=%7B%22type%22%3A%22car%22%2C%22action%22%3A%22(And.Hidden.N._.MultiView2Hidden.N._.Hidden.N._.SellType.%EC%9D%BC%EB%B0%98._.(C.CarType.Y._.(C.Manufacturer.%ED%98%84%EB%8C%80._.(C.ModelGroup.%EC%8A%A4%ED%83%80%EB%A0%89%EC%8A%A4._.(C.Model.%EA%B7%B8%EB%9E%9C%EB%93%9C%20%EC%8A%A4%ED%83%80%EB%A0%89%EC%8A%A4._.(Or.BadgeGroup.%EB%94%94%EC%A0%A4%202WD._.BadgeGroup.LPG%202WD._.BadgeGroup.%EB%94%94%EC%A0%A4%204WD.)))))_.Year.range(200800..).)%22%2C%22title%22%3A%22%ED%98%84%EB%8C%80%20%EA%B7%B8%EB%9E%9C%EB%93%9C%20%EC%8A%A4%ED%83%80%EB%A0%89%EC%8A%A4(07~17%EB%85%84)%22%2C%22toggle%22%3A%7B%22modelGroup%22%3A1%7D%2C%22layer%22%3A%22%22%2C%22sort%22%3A%22MobileModifiedDate%22%7D"
]

DETAIL_KEYWORDS = ["mdf/detail", "carid=", "/dt/car/"]
SEEN_FILE = Path("seen_links.json")

def load_seen_links():
    if SEEN_FILE.exists():
        try:
            with SEEN_FILE.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return {url: set(links) for url, links in data.items()}
        except:
            return {}
    return {}

def save_seen_links(seen_links):
    data = {url: list(links) for url, links in seen_links.items()}
    with SEEN_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def send_telegram_message(text):
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        r = requests.post(api_url, json=payload, timeout=10)
        r.raise_for_status()
    except:
        pass

def extract_car_links(html):
    all_urls = re.findall(r'https?://[^\s"\']+', html)
    car_urls = []
    for url in all_urls:
        if any(key in url for key in DETAIL_KEYWORDS):
            clean = url.split('"')[0].split("'")[0]
            car_urls.append(clean)
    return list(dict.fromkeys(car_urls).keys())

def check_once(seen_links):
    for idx, url in enumerate(FILTER_URLS, start=1):
        try:
            resp = requests.get(url, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            resp.raise_for_status()
        except:
            continue

        links = extract_car_links(resp.text)
        old_links = seen_links.get(url, set())

        if not old_links:
            seen_links[url] = set(links)
            continue

        new_links = [l for l in links if l not in old_links]

        for link in new_links:
            send_telegram_message(f"🔔 فلتر {idx} – لينك جديد:\n{link}")
            seen_links[url].add(link)

    save_seen_links(seen_links)

def main():
    seen_links = load_seen_links()
    while True:
        check_once(seen_links)
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
