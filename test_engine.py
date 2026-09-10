#!/usr/bin/env python3
"""Test script for Machine Context Engine."""

from app.main import MachineContextEngine


def main():
    """Test the engine with actual data files."""
    print("Initializing Machine Context Engine...")
    
    engine = MachineContextEngine(
        config_file="config.yaml",
        node_metadata_json="nodesfile.json",
        node_metadata_xml="BoilerModel2.NodeSet2 (1).xml"
    )
    
    print(f"\nNode registry loaded: {len(engine.get_node_registry().list_nodes())} nodes")
    print("Registered nodes:")
    for node in engine.get_node_registry().list_nodes()[:5]:
        print(f"  - {node.node_id}: {node.tag} ({node.data_type})")
    
    print("\n" + "="*60)
    print("Processing machine data...")
    print("="*60)
    
    context = engine.process("machine_data_5min.json")
    
    print(f"\nProcessing complete!")
    print(f"Context timestamp: {context.timestamp}")
    print(f"Machine state: {context.machine_state}")
    print(f"Health status: {context.health_status}")
    print(f"Health score: {context.health_score:.0f}/100")
    print(f"Active alarms: {context.active_alarm_count}")
    print(f"Anomalies: {context.anomaly_count}")
    print(f"Current readings: {len(context.current_readings)}")
    print(f"Unique tags: {len([r for r in context.current_readings.keys()])}")
    
    # Show unknown nodes
    unknown = engine.get_unknown_nodes()
    if unknown:
        print(f"\nUnknown nodes ({len(unknown)}):")
        for node_id in unknown[:5]:
            print(f"  - {node_id}")
    
    # Generate LLM context
    print("\n" + "="*60)
    print("LLM-READY CONTEXT:")
    print("="*60)
    llm_context = engine.get_llm_context()
    print(llm_context)
    
    print("\nCompact context:")
    print(engine.get_compact_context())


if __name__ == "__main__":
    main()
