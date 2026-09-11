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
    
    # Create app
    app = create_app(engine)
    
    # Run server
    print("\nStarting API server...")
    print("Visit: http://127.0.0.1:8000")
    
    uvicorn.run(app, host="127.0.0.1", port=8000)
