# The Cloud's Footprint

Mapping the world's data center infrastructure against the carbon, water, and land footprints of the electricity that powers it — grounded in [UNU-INWEH's 2026 global assessment of AI's environmental cost](https://doi.org/10.53328/INR26RMA002).

**[Open the live site →](https://fikalirous.github.io/data-center-lens/)**

Built with [VisQuill Lens](https://visquill.com/) — drag the lens across the map and it aggregates the data beneath it live into a bar chart of data centers, networks, and internet exchange points.

## About

In 2025, the world's data centers consumed an estimated 448 TWh of electricity — enough that if data centers were a country, they'd rank 11th globally. AI workloads alone accounted for roughly a fifth of that, projected to double by 2030. But the environmental cost of that electricity isn't uniform: it depends entirely on each country's electricity mix, and "low-carbon" doesn't automatically mean "low-water" or "low-land." This project pairs two views:

| View | What it shows |
|---|---|
| **Infrastructure lens** (interactive) | Data centers, networks, and exchange points per country — drag the lens to explore regions |
| **Electricity footprint map** | Carbon/water/land footprint intensity of major data center hub countries, relative to the global average — quoted directly from UNU-INWEH (2026) |

## Data dictionary

**Infrastructure lens:**

| Label | Column | Description | Source |
|---|---|---|---|
| Data Centers | `data_centers` | Number of PeeringDB-registered data center facilities in the country | World Bank Data360 (PeeringDB) |
| Networks | `total_networks` | Sum of networks (ASNs) present across all data center facilities in the country | PeeringDB API |
| Exchanges | `total_ix` | Sum of internet exchange points present across all data center facilities in the country | PeeringDB API |

The full dataset ([`data/country_level_dataset.csv`](data/country_level_dataset.csv)) also carries population, GDP per capita, internet/mobile adoption, and per-capita ecological footprint/biocapacity figures (Global Footprint Network) not currently wired into the map.

**Electricity footprint map:** carbon, water, and land footprint intensities for ~16 major data center hub countries, tiered (well below average → well above average) from figures quoted directly in UNU-INWEH (2026), Section 2.6 and Figure 9 (p.34–37), with Brazil's carbon figure from p.26. The country list and figures are inlined in `index.html` — see the `HUBS` array.

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

- **[UNU-INWEH (2026), *Environmental Cost of AI's Energy Use: Carbon, Water and Land Footprints*](https://doi.org/10.53328/INR26RMA002)** — the foundational source: data center electricity demand and country-level carbon/water/land footprint intensities. Aczel M., Chamanara S., Matin M., Farsi A., Marwala T., Madani K. (2026), United Nations University Institute for Water, Environment and Health, doi: 10.53328/INR26RMA002
- [World Bank Data360 — Interconnection Database (PeeringDB)](https://data360.worldbank.org/en/dataset/PEERING_DB) — data center counts per country
- [PeeringDB](https://www.peeringdb.com/) — facility-level network/exchange counts, aggregated to country totals here
- [World Bank World Development Indicators](https://data.worldbank.org/indicator) — supplementary GDP, internet use, mobile subscriptions, population figures in the full dataset
- [Global Footprint Network](https://data.footprintnetwork.org/) — supplementary ecological footprint and biocapacity figures in the full dataset
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
