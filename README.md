# The Cloud's Footprint

Mapping the world's data center infrastructure against each nation's ecological footprint, biocapacity, and digital economy.

**[Open the live site →](https://fikalirous.github.io/data-center-lens/)**

Built with [VisQuill Lens](https://visquill.com/) — drag up to three lens circles across the map and each aggregates the data beneath it live into a bar chart.

## About

This project maps where the internet's physical infrastructure — data centers and internet exchange points — actually sits, and asks a harder question: what does hosting that infrastructure cost the planet, and who is positioned to benefit from it? Every country in the dataset carries three angles, one per lens:

| Lens | Measures | What it shows |
|---|---|---|
| **Infrastructure** | Data Centers, Networks, Exchanges | Digital infrastructure density |
| **Resource Balance** | Footprint, Biocapacity, Balance | Whether the country consumes more than its land/sea can regenerate |
| **Digital Economy** | GDP/Capita, Internet %, Mobile/100 | Economic capacity and connectivity adoption |

## Data dictionary

| Label | Column | Description | Source |
|---|---|---|---|
| Data Centers | `data_centers` | Number of PeeringDB-registered data center facilities in the country | World Bank Data360 (PeeringDB) |
| Networks | `total_networks` | Sum of networks (ASNs) present across all data center facilities in the country | PeeringDB API |
| Exchanges | `total_ix` | Sum of internet exchange points present across all data center facilities in the country | PeeringDB API |
| Footprint | `footprint_total_earths` | Per-capita ecological footprint — Earths needed if everyone consumed like this country's average resident | Global Footprint Network |
| Biocapacity | `biocap_total_earths` | Per-capita biocapacity — Earths' worth of biologically productive land/sea provided per resident | Global Footprint Network (converted to per-capita "Earths") |
| Balance | `ecological_balance_earths` | Biocapacity − Footprint. Positive = ecological reserve, negative = ecological deficit | Derived |
| GDP/Capita | `gdp_per_capita_usd` | GDP per person, current US$ | World Bank WDI (`NY.GDP.PCAP.CD`) |
| Internet % | `internet_users_pct` | Share of population using the internet | World Bank WDI (`IT.NET.USER.ZS`) |
| Mobile/100 | `mobile_subs_per100` | Mobile cellular subscriptions per 100 people | World Bank WDI (`IT.CEL.SETS.P2`) |

The full dataset ([`data/country_level_dataset.csv`](data/country_level_dataset.csv)) also carries population, urbanisation, and per-category footprint/biocapacity breakdowns not currently wired into a lens.

## Repo structure

```
index.html            landing page (embeds the visual below)
visual/                exported VisQuill Lens app (self-contained, static)
data/
  country_level_dataset.csv     the merged, published dataset
  PEERING_DB.csv                 raw World Bank Data360 export (data center counts)
  PEERING_DB_DATADICT.csv        World Bank's column definitions for the above
scripts/
  fetch_peeringdb_facilities.py  pulls facility-level data from the PeeringDB API
  build_country_dataset.py       merges all sources into data/country_level_dataset.csv
```

## Reproducing the dataset

`build_country_dataset.py` expects two raw source files that aren't committed to
this repo (see **Data sources & licensing** below) — download them yourself, then run:

```bash
python scripts/fetch_peeringdb_facilities.py    # writes data/peeringdb_facilities.csv
python scripts/build_country_dataset.py          # writes data/country_level_dataset.csv
```

`build_country_dataset.py` also expects `data/Ecological_footprint_Compare_Countries.csv`
and `data/Biocapacity_Compare_Countries.csv`, exported from the Global Footprint Network's
[data explorer](https://data.footprintnetwork.org/#/compareCountries?type=earth&cn=all&yr=2023)
(switch the `type` param to biocapacity for the second file).

## Sources & credits

- [World Bank Data360 — Interconnection Database (PeeringDB)](https://data360.worldbank.org/en/dataset/PEERING_DB) — data center counts per country
- [PeeringDB](https://www.peeringdb.com/) — facility-level network/exchange counts, aggregated to country totals here
- [World Bank World Development Indicators](https://data.worldbank.org/indicator) — GDP, internet use, mobile subscriptions, population, urbanisation
- [Global Footprint Network](https://data.footprintnetwork.org/) — ecological footprint and biocapacity by country
- [mledoze/countries](https://github.com/mledoze/countries) — country ISO codes and centroids (MIT licensed)
- [VisQuill Lens](https://visquill.com/) — the visualization engine

## Data sources & licensing

World Bank data is openly licensed (CC BY 4.0) and included directly in `data/`. PeeringDB's
terms of use restrict systematic redistribution of their raw database, and the Global
Footprint Network CSVs are exports from their data explorer without a clear open
redistribution license — so those three raw source files are **not** committed here.
Only the country-level aggregates *derived* from them (in `country_level_dataset.csv`,
attributed above) are published. To reproduce them yourself, see
**Reproducing the dataset** above.

The standalone visual is free to use with VisQuill attribution — see
[visquill.com/licence](https://visquill.com/licence).
