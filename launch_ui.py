#!/usr/bin/env python3
"""Launch the browser-based operator dashboard."""
import uvicorn

from app.main import MachineContextEngine
from app.api.routes import create_app


if __name__ == "__main__":
    engine = MachineContextEngine(
        config_file="config.yaml",
        node_metadata_json="nodesfile.json",
        node_metadata_xml="BoilerModel2.NodeSet2 (1).xml",
    )
    uvicorn.run(create_app(engine), host="127.0.0.1", port=8000)
