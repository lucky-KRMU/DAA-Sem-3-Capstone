"""
Script to generate and persist sample datasets for all benchmark scales:
Small, Medium, Large, and Stress.
"""

import os
from src.dataset_generator import (
    generate_city_road_network,
    generate_parcels,
    export_parcels_csv,
    export_dataset_json
)


def main():
    os.makedirs("data", exist_ok=True)
    os.makedirs("charts", exist_ok=True)
    os.makedirs("docs", exist_ok=True)

    configs = [
        {
            "name": "small",
            "parcels": 15,
            "nodes": 8,
            "capacity": 35,
            "seed": 42
        },
        {
            "name": "medium",
            "parcels": 100,
            "nodes": 25,
            "capacity": 120,
            "seed": 101
        },
        {
            "name": "large",
            "parcels": 500,
            "nodes": 50,
            "capacity": 350,
            "seed": 202
        },
        {
            "name": "stress",
            "parcels": 1000,
            "nodes": 80,
            "capacity": 600,
            "seed": 303
        }
    ]

    for cfg in configs:
        prefix = cfg["name"]
        print(f"Generating {prefix.capitalize()} dataset ({cfg['parcels']} parcels, {cfg['nodes']} nodes)...")
        graph = generate_city_road_network(num_nodes=cfg["nodes"], seed=cfg["seed"])
        parcels = generate_parcels(num_parcels=cfg["parcels"], num_nodes=cfg["nodes"], seed=cfg["seed"] + 1)

        meta = {
            "dataset_name": f"{prefix}_dataset",
            "num_parcels": cfg["parcels"],
            "num_nodes": cfg["nodes"],
            "recommended_capacity": cfg["capacity"],
            "seed": cfg["seed"]
        }

        json_path = f"data/{prefix}_dataset.json"
        csv_path = f"data/{prefix}_dataset.csv"

        export_dataset_json(parcels, graph, json_path, metadata=meta)
        export_parcels_csv(parcels, csv_path)
        print(f"  -> Saved {json_path} and {csv_path}")

    # Also save standard city_graph.json
    base_graph = generate_city_road_network(num_nodes=25, seed=101)
    with open("data/city_graph.json", "w", encoding="utf-8") as f:
        import json
        json.dump(base_graph.to_dict(), f, indent=2)
    print("  -> Saved data/city_graph.json")


if __name__ == "__main__":
    main()
