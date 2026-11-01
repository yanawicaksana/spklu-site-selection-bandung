"""EV charging station (SPKLU) site selection, Kota Bandung, Indonesia.

Computes charging coverage gaps per district (kecamatan), joins population,
and compares four candidate districts. Run from the repo root:

    python scripts/analysis.py

Inputs: data/raw/   Outputs: data/processed/ and outputs/
"""
from pathlib import Path
import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, PROC, OUT = ROOT / "data/raw", ROOT / "data/processed", ROOT / "outputs"
UTM = 32748              # WGS 84 / UTM zone 48S (metres)
RADII_M = [1000, 2000]   # service-radius assumptions
CANDIDATES = ["BOJONGLOA KALER", "KIARACONDONG", "ANTAPANI", "CIBIRU"]


def main():
    PROC.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)

    # 1. District boundaries (30 kecamatan, 2020)
    dist = gpd.read_file(RAW / "bandung_district_boundaries_2020.geojson").to_crs(UTM)
    dist = dist.rename(columns={"Kecamatan": "district", "Kode_Kec": "district_code"})
    dist["area_km2"] = (dist.area / 1e6).round(2)

    # 2. Charging stations: drop flagged coordinates, keep stations within 3 km of the city
    st = pd.read_csv(RAW / "spklu_stations_indonesia.csv")
    st = st[~st.quality_flags.fillna("").str.contains("coord_review|coord_unparseable")]
    st = gpd.GeoDataFrame(st, geometry=gpd.points_from_xy(st.longitude, st.latitude), crs=4326).to_crs(UTM)
    st = st[st.within(dist.union_all().buffer(3000))]   # neighbours also serve the city edge
    st["is_public"] = st.provider_type != "Automaker / dealership"  # dealer chargers are usually brand-only

    inside = gpd.sjoin(st, dist[["district", "geometry"]], predicate="within")
    inside.drop(columns=["geometry", "index_right"]).to_csv(PROC / "spklu_bandung_city.csv", index=False)

    # 3. Station counts and coverage (share of district area within radius of a public charger)
    dist["n_spklu"] = dist.district.map(inside.groupby("district").size()).fillna(0).astype(int)
    dist["n_public_spklu"] = dist.district.map(inside[inside.is_public].groupby("district").size()).fillna(0).astype(int)
    public_sites = st[st.is_public].drop_duplicates(["latitude", "longitude"])
    for r in RADII_M:
        served = public_sites.buffer(r).union_all()
        dist[f"public_coverage_{r // 1000}km_pct"] = (dist.intersection(served).area / dist.area * 100).round(1)

    # 4. Population (BPS 2024)
    pop = pd.read_csv(RAW / "bps_population_by_district_bandung_2024.csv").iloc[:30, [0, 1, 4]]
    pop.columns = ["name", "population", "density_per_km2"]
    pop["district"] = pop.name.str.upper().str.replace("ASTANAANYAR", "ASTANA ANYAR")
    dist = dist.merge(pop[["district", "population", "density_per_km2"]], on="district", how="left")
    assert dist.population.notna().all(), "unmatched district names"
    # rough estimate: assumes population spread evenly within each district
    dist["pop_outside_1km_est"] = (dist.population * (1 - dist.public_coverage_1km_pct / 100)).round(0).astype(int)

    dist.to_crs(4326).to_file(PROC / "bandung_districts_spklu_population.geojson", driver="GeoJSON")
    table = dist.drop(columns="geometry").sort_values("public_coverage_1km_pct")
    table.to_csv(OUT / "summary_by_district.csv", index=False)

    # 5. Candidate comparison
    cols = ["district", "population", "density_per_km2", "n_public_spklu", "public_coverage_1km_pct", "pop_outside_1km_est"]
    cand = table[table.district.isin(CANDIDATES)][cols].sort_values("density_per_km2", ascending=False)
    cand.to_csv(OUT / "candidate_comparison.csv", index=False)

    # 6. GEO MAPID Site Selection grid: class counts (labels translated)
    grid = pd.read_csv(RAW / "geomapid_site_selection_grid.csv")
    labels = {"Sangat Sesuai": "Highly suitable", "Sesuai": "Suitable", "Cukup Sesuai": "Moderately suitable",
              "Tidak Sesuai": "Not suitable", "Sangat Tidak Sesuai": "Highly unsuitable"}
    classes = grid.Class.map(labels).value_counts().rename_axis("class").reset_index(name="n_cells")
    classes.to_csv(OUT / "geomapid_grid_classes.csv", index=False)

    print(f"Stations in Kota Bandung: {len(inside)} ({inside.is_public.sum()} public, {(~inside.is_public).sum()} dealer)")
    print(cand.to_string(index=False))
    print(classes.to_string(index=False))


if __name__ == "__main__":
    main()
