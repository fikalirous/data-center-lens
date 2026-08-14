"""
Fetch facility-level data from the public PeeringDB API and shape it for
VisQuill Lens (needs latitude/longitude + numeric measures per row).

PeeringDB's public GET endpoints require no authentication. Docs:
https://www.peeringdb.com/apidocs/
"""

import csv
import json
import time
import urllib.request

API_URL = "https://www.peeringdb.com/api/fac"
PAGE_LIMIT = 50000  # comfortably above the total facility count; API returns all in one page
OUTPUT_FILE = "data/peeringdb_facilities.csv"  # run from repo root

# Note: this script's output is a bulk export of PeeringDB's database and is
# kept local / gitignored rather than committed — see PeeringDB's terms of
# use on systematic redistribution. build_country_dataset.py only publishes
# the country-level aggregates derived from it.

FIELDS = [
    "id",
    "name",
    "city",
    "country",
    "state",
    "latitude",
    "longitude",
    "net_count",
    "ix_count",
]


def fetch_page(url):
    req = urllib.request.Request(url, headers={"User-Agent": "personal-project-data-fetch/1.0"})
    backoff = 5
    while True:
        try:
            with urllib.request.urlopen(req) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as e:
            if e.code == 429 and backoff <= 60:
                print(f"rate limited, waiting {backoff}s...")
                time.sleep(backoff)
                backoff *= 2
                continue
            raise


def fetch_all_facilities():
    payload = fetch_page(f"{API_URL}?limit={PAGE_LIMIT}")
    facilities = payload.get("data", [])
    print(f"fetched {len(facilities)} facilities")
    return facilities


def main():
    facilities = fetch_all_facilities()

    rows = [f for f in facilities if f.get("latitude") is not None and f.get("longitude") is not None]
    skipped = len(facilities) - len(rows)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for fac in rows:
            writer.writerow({k: fac.get(k) for k in FIELDS})

    print(f"\nWrote {len(rows)} facilities with coordinates to {OUTPUT_FILE}")
    print(f"Skipped {skipped} facilities with no lat/lon")


if __name__ == "__main__":
    main()
