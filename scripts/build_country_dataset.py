"""
Build a country-level dataset for VisQuill Lens: one row per country with
a stable lat/lon centroid plus several numeric measures (data center
presence + a few development indicators) so a dragged lens has multiple
interesting factors to aggregate and chart.

Sources (all public, no auth required):
- Country centroids/ISO codes: mledoze/countries (MIT licensed, GitHub)
- Data center count per country: local PEERING_DB.csv (World Bank Data360)
- Facility-level network/exchange counts: local peeringdb_facilities.csv
- Population, GDP per capita, internet use %, urban pop %, mobile subs:
  World Bank Open Data API (api.worldbank.org)
- Ecological footprint (demand) and biocapacity (supply): local CSVs
  exported from Global Footprint Network's data explorer
  (data.footprintnetwork.org)
"""

import csv
import json
import time
import urllib.request

COUNTRIES_URL = "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
WB_INDICATOR_URL = "https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&per_page=20000&mrv=10"

INDICATORS = {
    "population": "SP.POP.TOTL",
    "gdp_per_capita_usd": "NY.GDP.PCAP.CD",
    "internet_users_pct": "IT.NET.USER.ZS",
    "urban_pop_pct": "SP.URB.TOTL.IN.ZS",
    "mobile_subs_per100": "IT.CEL.SETS.P2",
}

# Run from repo root: python scripts/build_country_dataset.py
# LOCAL_FACILITIES_CSV, LOCAL_FOOTPRINT_CSV and LOCAL_BIOCAPACITY_CSV are raw
# third-party exports not committed to this repo (see fetch_peeringdb_facilities.py
# and README for how to obtain them) — only their derived aggregates are published.
LOCAL_WB_PEERING_CSV = "data/PEERING_DB.csv"
LOCAL_FACILITIES_CSV = "data/peeringdb_facilities.csv"
LOCAL_FOOTPRINT_CSV = "data/Ecological_footprint_Compare_Countries.csv"
LOCAL_BIOCAPACITY_CSV = "data/Biocapacity_Compare_Countries.csv"
OUTPUT_FILE = "data/country_level_dataset.csv"

# Global Footprint Network's per-capita ecological footprint (demand side),
# broken down by consumption category (source column -> output column name).
FOOTPRINT_FIELDS = {
    "Total": "footprint_total_earths",
    "Carbon": "footprint_carbon",
    "Cropland": "footprint_cropland",
    "Grazing Land": "footprint_grazing_land",
    "Forest Products": "footprint_forest_products",
    "Fishing Grounds": "footprint_fishing_grounds",
    "Built-up Land": "footprint_built_up_land",
}

# Global Footprint Network's biocapacity (supply side) — national totals in
# global hectares (GHA), not per capita. "Carbon" biocapacity is always 0
# under this accounting (land doesn't supply carbon absorption capacity as a
# distinct category), so it's dropped rather than carried as dead weight.
BIOCAPACITY_FIELDS = {
    "Total": "biocap_total_gha",
    "Cropland": "biocap_cropland_gha",
    "Grazing Land": "biocap_grazing_land_gha",
    "Forest Products": "biocap_forest_products_gha",
    "Fishing Grounds": "biocap_fishing_grounds_gha",
    "Built-up Land": "biocap_built_up_land_gha",
}


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "personal-project-data-fetch/1.0"})
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def load_countries():
    data = fetch_json(COUNTRIES_URL)
    countries = {}
    iso2_to_iso3 = {}
    for c in data:
        iso3 = c["cca3"]
        latlng = c.get("latlng") or [None, None]
        countries[iso3] = {
            "iso3": iso3,
            "iso2": c["cca2"],
            "name": c["name"]["common"],
            "latitude": latlng[0],
            "longitude": latlng[1],
        }
        iso2_to_iso3[c["cca2"]] = iso3
    return countries, iso2_to_iso3


def load_data_center_counts():
    counts = {}
    with open(LOCAL_WB_PEERING_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso3 = row["REF_AREA"]
            try:
                counts[iso3] = float(row["OBS_VALUE"])
            except (ValueError, KeyError):
                continue
    return counts


def load_facility_aggregates(iso2_to_iso3):
    agg = {}
    with open(LOCAL_FACILITIES_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso3 = iso2_to_iso3.get(row["country"])
            if not iso3:
                continue
            bucket = agg.setdefault(iso3, {"facility_count": 0, "total_networks": 0, "total_ix": 0})
            bucket["facility_count"] += 1
            bucket["total_networks"] += int(row["net_count"] or 0)
            bucket["total_ix"] += int(row["ix_count"] or 0)
    return agg


def load_footprint(iso2_to_iso3):
    results = {name: {} for name in FOOTPRINT_FIELDS.values()}
    with open(LOCAL_FOOTPRINT_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso3 = iso2_to_iso3.get(row["isoa2"])
            if not iso3:
                continue
            for src_col, out_col in FOOTPRINT_FIELDS.items():
                value = row.get(src_col)
                if value:
                    results[out_col][iso3] = float(value)
    return results


def load_biocapacity(iso2_to_iso3):
    results = {name: {} for name in BIOCAPACITY_FIELDS.values()}
    with open(LOCAL_BIOCAPACITY_CSV, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            iso3 = iso2_to_iso3.get(row["isoa2"])
            if not iso3:
                continue
            for src_col, out_col in BIOCAPACITY_FIELDS.items():
                value = row.get(src_col)
                if value:
                    results[out_col][iso3] = float(value)
    return results


def load_wb_indicators():
    # mrv=10 pulls the last 10 years per indicator; many countries lag on
    # recent survey-based indicators (e.g. internet use), so keep each
    # country's most recent non-null value rather than a single fixed year.
    results = {name: {} for name in INDICATORS}
    for name, code in INDICATORS.items():
        payload = fetch_json(WB_INDICATOR_URL.format(code=code))
        latest_date = {}
        for row in payload[1]:
            iso3 = row.get("countryiso3code")
            value = row.get("value")
            date = row.get("date")
            if not iso3 or value is None:
                continue
            if iso3 not in latest_date or date > latest_date[iso3]:
                latest_date[iso3] = date
                results[name][iso3] = value
        print(f"loaded {len(results[name])} values for {name}")
        time.sleep(0.5)
    return results


def main():
    countries, iso2_to_iso3 = load_countries()
    dc_counts = load_data_center_counts()
    facility_agg = load_facility_aggregates(iso2_to_iso3)
    wb_indicators = load_wb_indicators()
    footprint = load_footprint(iso2_to_iso3)
    biocapacity = load_biocapacity(iso2_to_iso3)

    population = wb_indicators["population"]
    biocap_total_gha = biocapacity["biocap_total_gha"]

    # Derive a global per-capita biocapacity baseline ("1 Earth" in GHA) from
    # this same dataset, so biocapacity can be expressed in the same "Earths"
    # unit as the footprint data and compared directly against it.
    overlap = [iso3 for iso3 in biocap_total_gha if iso3 in population]
    world_biocap_per_capita_gha = (
        sum(biocap_total_gha[iso3] for iso3 in overlap) / sum(population[iso3] for iso3 in overlap)
    )
    print(f"derived world biocapacity baseline: {world_biocap_per_capita_gha:.3f} gha/person (1 Earth)")

    biocap_per_capita_gha = {}
    biocap_total_earths = {}
    for iso3, total_gha in biocap_total_gha.items():
        if iso3 not in population or population[iso3] == 0:
            continue
        per_capita = total_gha / population[iso3]
        biocap_per_capita_gha[iso3] = per_capita
        biocap_total_earths[iso3] = per_capita / world_biocap_per_capita_gha

    fieldnames = [
        "iso3", "iso2", "country", "latitude", "longitude",
        "data_centers", "facility_count", "total_networks", "total_ix",
        *INDICATORS.keys(),
        *FOOTPRINT_FIELDS.values(),
        *BIOCAPACITY_FIELDS.values(),
        "biocap_per_capita_gha", "biocap_total_earths", "ecological_balance_earths",
    ]

    rows = []
    for iso3, c in countries.items():
        if c["latitude"] is None:
            continue
        fac = facility_agg.get(iso3, {})
        row = {
            "iso3": iso3,
            "iso2": c["iso2"],
            "country": c["name"],
            "latitude": c["latitude"],
            "longitude": c["longitude"],
            "data_centers": dc_counts.get(iso3, ""),
            "facility_count": fac.get("facility_count", ""),
            "total_networks": fac.get("total_networks", ""),
            "total_ix": fac.get("total_ix", ""),
        }
        for name in INDICATORS:
            row[name] = wb_indicators[name].get(iso3, "")
        for out_col in FOOTPRINT_FIELDS.values():
            row[out_col] = footprint[out_col].get(iso3, "")
        for out_col in BIOCAPACITY_FIELDS.values():
            row[out_col] = biocapacity[out_col].get(iso3, "")

        row["biocap_per_capita_gha"] = biocap_per_capita_gha.get(iso3, "")
        row["biocap_total_earths"] = biocap_total_earths.get(iso3, "")
        footprint_val = footprint["footprint_total_earths"].get(iso3)
        biocap_val = biocap_total_earths.get(iso3)
        row["ecological_balance_earths"] = (
            biocap_val - footprint_val if footprint_val is not None and biocap_val is not None else ""
        )
        rows.append(row)

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {len(rows)} countries to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
