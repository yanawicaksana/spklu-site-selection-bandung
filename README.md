# Where should Bandung put its next EV charging station?

A site-selection analysis for public EV charging stations (*SPKLU, Stasiun Pengisian Kendaraan Listrik Umum*) in Kota Bandung, Indonesia, built with open data, Python and GEO MAPID.

**Recommendation:** Bojongloa Kaler district, around Jamika – Suka Asih. It is Bandung's most densely populated district (41,711 people/km²), it has no public charger, and it is the only area outside the city centre that ranks in GEO MAPID's top 10 suitability cells. Kiaracondong is the second priority.

![GEO MAPID site selection grid with existing chargers](figures/02_geomapid_site_selection_grid.png)

## Why this question

- Indonesia had 4,778 public chargers at 3,093 locations in December 2025, against a target of about 192,000 by 2034 ([CNN Indonesia, 2026](https://cnnindonesia.com/otomotif/20260203162604-603-1324154/indonesia-punya-4778-spklu-saat-ini-ditargetkan-192-ribu-pada-2034)).
- Kota Bandung has 67 chargers (June 2026). 21 of them sit in just 3 of its 30 districts (Sumur Bandung, Bandung Wetan, Lengkong), the hotel and business core.
- 16 of the 67 are at car dealerships and are usually reserved for one brand, so only 51 serve the general public.

![Existing EV charging stations in Bandung, mapped in GEO MAPID](figures/00_geomapid_charger_locations.png)

*Existing chargers cluster in the city centre and along Jl. Soekarno-Hatta. The south-west, between Kopo and the centre, is visibly empty.*

## Data

| Dataset | Use | Source | Licence / terms |
| --- | --- | --- | --- |
| Geocoded SPKLU stations, Indonesia (3,029 stations, retrieved 16 June 2026) | Charger locations, operator type | Wiputra, R. (2026). [Mendeley Data, DOI 10.17632/z2bvd5r574.1](https://data.mendeley.com/datasets/z2bvd5r574/1), from petaspklu.id / PT PLN | CC BY-NC 3.0 |
| Population and density by district, 2024 | Demand | [BPS Kota Bandung](https://bandungkota.bps.go.id/) | Public statistics, cite BPS |
| District (kecamatan) boundaries, 2020 | Spatial units | [Alf-Anas/batas-administrasi-indonesia](https://github.com/Alf-Anas/batas-administrasi-indonesia) | Check the source repo before reuse |
| Points of interest and grid-level population density | Suitability inputs | GEO MAPID demography and POI layers (accessed October 2026) | Follow GEO MAPID terms |
| Site Selection grid export (312 hexagon cells) | Suitability scores | Produced in GEO MAPID Site Selection | Follow GEO MAPID terms |

## Method

1. **Filter** the national charger dataset to Kota Bandung (67 stations) and drop records with flagged coordinates.
2. **Coverage gap:** buffer every *public* charger by 1 km and 2 km, then compute the share of each district's area inside that radius (straight-line distance, UTM 48S).
3. **Demand:** join 2024 BPS population and density per district.
4. **Suitability (GEO MAPID Site Selection):** hexagon grid scored on population density (weight 3) and five POI categories, all positive: retail & trade (2), transportation (2), hotels (1), health (1), food & beverage (1).
5. **Gap filter:** overlay existing chargers on the grid. High-scoring cells with no public charger nearby become candidate sites.
6. **Compare** four low-coverage candidate districts.

## Results

| District | Population | Density (people/km²) | Public chargers | Area within 1 km of a public charger | GEO MAPID grid |
| --- | --- | --- | --- | --- | --- |
| **Bojongloa Kaler** | 126,385 | 41,711 | 0 | 9.4% | Green, cells ranked 4 and 9 |
| Kiaracondong | 133,063 | 21,742 | 0 | 9.2% | Yellow (moderate) |
| Antapani | 82,350 | 21,728 | 0 | 4.8% | Yellow–orange |
| Cibiru | 79,452 | 12,572 | 1 | 21.0% | Orange–red |

- Only 14 of 312 grid cells (4.5%) are *suitable* or *highly suitable*.
- 7 of the top 10 cells are in the city centre, which already has the most chargers. A suitability model alone would put new chargers where they are least needed; the gap filter is what moves the answer.
- Cell rank 4 (score 78.8/100) around Jamika – Suka Asih has the highest density in the grid (68,753 people/km²) and 211 POIs, with no public charger nearby.

| Share of each district within 1 km of a public charger (red = under 25%) | Site Selection formula |
| --- | --- |
| ![Coverage by district](figures/01_geomapid_coverage_by_district.png) | ![Formula panel](figures/03_geomapid_formula_panel.png) |

Full Site Selection results, with the top 10 cells and their scores, are in [`result_selection/`](result_selection/README.md).

An interactive map of chargers and coverage is in [`docs/index.html`](docs/index.html) (publish it with GitHub Pages from the `docs/` folder).

## Limitations

- GEO MAPID's formula does not include existing chargers, so the gap filter was applied by overlay.
- POI weights add up to 7 against 3 for population, which tilts scores towards commercial areas.
- Coverage uses straight-line 1 km buffers and assumes population is spread evenly within each district.
- Data years differ: population 2024, chargers June 2026, boundaries 2020.
- EV ownership by district is not public, so population density stands in for demand.
- Grid cell locations are read from the GEO MAPID map labels; the export has no coordinates.

## Reproduce

The coverage-gap analysis can be fully rerun from open data:

```bash
pip install -r requirements.txt
python scripts/analysis.py
```

The suitability step (step 4) needs GEO MAPID, because its POI and grid population data are not open. Its exported results are included in `data/raw/geomapid_site_selection_grid.csv`, so the scores can still be checked.

```
data/raw/          input data (see table above)
data/processed/    Bandung chargers + districts with coverage and population (CSV, GeoJSON)
outputs/           summary_by_district.csv, candidate_comparison.csv, geomapid_grid_classes.csv
figures/           GEO MAPID maps and screenshots
result_selection/  GEO MAPID Site Selection maps and top-cell table
docs/index.html    interactive map
scripts/analysis.py
```

## Credits

Analysis by Yana Wicaksana as part of the GEO MAPID *Spatial Data & Analysis Foundation* module (October 2026). Charger data © R. Wiputra / PT PLN (Persero) under CC BY-NC 3.0; population data © BPS Kota Bandung.
