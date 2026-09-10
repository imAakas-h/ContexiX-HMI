#!/usr/bin/env python3
"""Launch REST API server."""
import uvicorn
from app.main import MachineContextEngine
from app.api.routes import create_app


if __name__ == "__main__":
    # Initialize engine
    engine = MachineContextEngine(
        config_file="config.yaml",
        node_metadata_json="nodesfile.json",
        node_metadata_xml="BoilerModel2.NodeSet2 (1).xml"
    )
    
    # Pre-process data
    print("Pre-processing machine data...")
    context = engine.process("machine_data_5min.json")
    print(f"Context ready: {context.machine_state} | Health: {context.health_score:.0f}")
    
    # Create app
    app = create_app(engine)
    
    # Run server
    print("\nStarting API server...")
    print("Visit: http://localhost:8000/docs")
    print("Health: http://localhost:8000/health")
    print("Context: http://localhost:8000/context")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
