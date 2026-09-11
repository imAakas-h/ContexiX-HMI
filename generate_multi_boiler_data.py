"""Generate multi-boiler machine data from existing data."""
import json
from datetime import datetime
from pathlib import Path
import random

def generate_multi_boiler_data():
    """Generate data for 3 boilers by interpolating existing data."""
    
    # Load original data
    with open("machine_data_5min.json") as f:
        original_data = json.load(f)
    
    # Create new data structure with 3 boilers
    multi_boiler_data = {
        "collection_info": {
            "source": "opc.tcp://localhost:4840/mce/server/",
            "duration_seconds": 300,
            "sampling_interval_seconds": 1,
            "start_time": original_data["collection_info"]["start_time"],
            "end_time": original_data["collection_info"]["end_time"],
            "boilers": ["Boiler1", "Boiler2", "Boiler3"]
        },
        "data": []
    }
    
    # Boiler-specific variations (multipliers and offsets)
    boiler_params = {
        "Boiler1": {"mult": 1.0, "offset": 0, "name": "Boiler 1 - Main"},
        "Boiler2": {"mult": 0.95, "offset": 2, "name": "Boiler 2 - Secondary"},
        "Boiler3": {"mult": 1.05, "offset": -1, "name": "Boiler 3 - Backup"}
    }
    
    # For each timestamp and boiler, generate data
    readings_by_timestamp = {}
    
    # Group original readings by timestamp
    for reading in original_data["data"]:
        ts = reading["timestamp"]
        if ts not in readings_by_timestamp:
            readings_by_timestamp[ts] = []
        readings_by_timestamp[ts].append(reading)
    
    # Generate data for each boiler
    boiler_node_id_base = {"Boiler1": 2, "Boiler2": 100, "Boiler3": 200}
    
    for timestamp, readings_at_ts in readings_by_timestamp.items():
        for boiler_name, params in boiler_params.items():
            node_id_base = boiler_node_id_base[boiler_name]
            
            for reading in readings_at_ts:
                new_reading = {
                    "timestamp": timestamp,
                    "boiler": boiler_name,
                    "boiler_name": params["name"],
                    "node_id": f"ns=2;i={node_id_base + int(reading['node_id'].split(';i=')[1])}",
                    "tag": reading["tag"],
                    "datatype": reading["datatype"],
                    "quality": reading["quality"]
                }
                
                # Apply boiler-specific variations to numeric values
                if isinstance(reading["value"], (int, float)):
                    # Add boiler-specific noise and variation
                    noise = random.uniform(-0.5, 0.5)
                    new_reading["value"] = round(
                        (reading["value"] * params["mult"]) + params["offset"] + noise, 
                        2
                    )
                else:
                    # String values stay the same
                    new_reading["value"] = reading["value"]
                
                multi_boiler_data["data"].append(new_reading)
    
    # Save new data
    with open("machine_data_multi_boiler.json", "w") as f:
        json.dump(multi_boiler_data, f, indent=2)
    
    print("✅ Multi-boiler data generated: machine_data_multi_boiler.json")
    print(f"   Boilers: {multi_boiler_data['collection_info']['boilers']}")
    print(f"   Total readings: {len(multi_boiler_data['data'])}")

if __name__ == "__main__":
    generate_multi_boiler_data()
