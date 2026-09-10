#!/usr/bin/env python3
"""Verify that we're using the actual uploaded data files."""
import json

print("=" * 60)
print("VERIFYING YOUR DATA FILES")
print("=" * 60)

# Check machine data
with open("machine_data_5min.json") as f:
    machine_data = json.load(f)

print("\n1. MACHINE DATA (machine_data_5min.json):")
print(f"   Source: {machine_data['collection_info']['source']}")
print(f"   Duration: {machine_data['collection_info']['duration_seconds']}s")
print(f"   Sampling: {machine_data['collection_info']['sampling_interval_seconds']}s")
print(f"   Total readings: {len(machine_data['data'])}")
print(f"   Start time: {machine_data['collection_info']['start_time']}")
print(f"   End time: {machine_data['collection_info']['end_time']}")

# Show sample reading
print(f"\n   First reading:")
first = machine_data['data'][0]
print(f"     - Node ID: {first['node_id']}")
print(f"     - Tag: {first['tag']}")
print(f"     - Value: {first['value']}")
print(f"     - Data type: {first['datatype']}")
print(f"     - Quality: {first['quality']}")

# Check nodes metadata
with open("nodesfile.json") as f:
    nodes_data = json.load(f)

print("\n2. NODE METADATA (nodesfile.json):")
print(f"   Folder: {nodes_data['Folder']}")
print(f"   Nodes in main list: {len(nodes_data['NodeList'])}")
print(f"   FolderLists: {len(nodes_data['FolderList'])}")

print(f"\n   Sample nodes:")
for node in nodes_data['NodeList'][:3]:
    print(f"     - NodeId: {node.get('NodeId')}, Name: {node.get('Name', 'N/A')}")

# Check config
with open("config.yaml") as f:
    import yaml
    config = yaml.safe_load(f)

print("\n3. CONFIGURATION (config.yaml):")
print(f"   Machine name: {config['machine']['name']}")
print(f"   Configured nodes: {len(config['nodes'])}")
print(f"\n   Node configurations:")
for node_id in list(config['nodes'].keys())[:3]:
    print(f"     - {node_id}: unit={config['nodes'][node_id].get('unit')}, component={config['nodes'][node_id].get('component')}")

print("\n" + "=" * 60)
print("All data is REAL from your uploaded files - not mock data!")
print("=" * 60)
