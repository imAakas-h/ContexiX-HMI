"""JSON adapter for reading machine data and metadata."""
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.inputs.base_adapter import DataAdapter, MetadataAdapter
from app.models.reading import MachineDataCollection, MachineReading, QualityStatus
from app.models.node import NodeMetadata, NodeMetadataRegistry


class JSONDataAdapter(DataAdapter):
    """Reads machine_data_5min.json format."""
    
    def read(self, source: str) -> dict[str, Any]:
        """Read JSON file."""
        with open(source, 'r') as f:
            return json.load(f)
    
    def parse_collection(self, source: str) -> MachineDataCollection:
        """Parse machine data JSON into MachineDataCollection."""
        data = self.read(source)
        
        # Extract collection info
        collection_info = data.get("collection_info", {})
        
        # Parse timestamps
        start_time = datetime.fromisoformat(
            collection_info.get("start_time", "").replace("Z", "+00:00")
        )
        end_time = datetime.fromisoformat(
            collection_info.get("end_time", "").replace("Z", "+00:00")
        )
        
        # Parse readings
        readings = []
        for raw_reading in data.get("data", []):
            reading = self._parse_reading(raw_reading)
            if reading:
                readings.append(reading)
        
        # Create collection
        return MachineDataCollection(
            source=collection_info.get("source", "unknown"),
            duration_seconds=collection_info.get("duration_seconds", 0),
            sampling_interval_seconds=collection_info.get("sampling_interval_seconds", 0),
            start_time=start_time,
            end_time=end_time,
            readings=readings
        )
    
    def _parse_reading(self, raw_reading: dict[str, Any]) -> MachineReading | None:
        """Convert raw reading dict to MachineReading."""
        try:
            timestamp = datetime.fromisoformat(
                raw_reading.get("timestamp", "").replace("Z", "+00:00")
            )
            
            # Parse quality string: "StatusCode(value=0)" -> "GOOD"
            quality_str = raw_reading.get("quality", "")
            quality = self._parse_quality(quality_str)
            
            return MachineReading(
                timestamp=timestamp,
                node_id=raw_reading.get("node_id", ""),
                tag=raw_reading.get("tag", ""),
                value=raw_reading.get("value"),
                data_type=raw_reading.get("datatype", "Unknown").capitalize(),
                quality=quality,
                unit=None,  # Will be enriched from metadata
                boiler=raw_reading.get("boiler")  # Support boiler field from multi-boiler data
            )
        except Exception as e:
            print(f"Error parsing reading: {e}")
            return None
    
    def _parse_quality(self, quality_str: str) -> str:
        """Convert StatusCode string to quality level."""
        if "value=0" in quality_str:
            return QualityStatus.GOOD
        elif "value=1" in quality_str or "UNCERTAIN" in quality_str:
            return QualityStatus.UNCERTAIN
        elif "BAD" in quality_str or "value=2" in quality_str:
            return QualityStatus.BAD
        else:
            return QualityStatus.UNKNOWN


class JSONMetadataAdapter(MetadataAdapter):
    """Reads nodesfile.json format."""
    
    def read(self, source: str) -> dict[str, Any]:
        """Read JSON file."""
        with open(source, 'r') as f:
            return json.load(f)
    
    def parse_metadata(self, source: str) -> NodeMetadataRegistry:
        """Parse node metadata JSON into NodeMetadataRegistry."""
        data = self.read(source)
        registry = NodeMetadataRegistry()
        
        # Parse nodes from NodeList
        for raw_node in data.get("NodeList", []):
            metadata = self._parse_node(raw_node)
            if metadata:
                registry.add_node(metadata)
        
        # Parse nodes from FolderList recursively
        for folder in data.get("FolderList", []):
            for raw_node in folder.get("NodeList", []):
                metadata = self._parse_node(raw_node)
                if metadata:
                    registry.add_node(metadata)
        
        return registry
    
    def _parse_node(self, raw_node: dict[str, Any]) -> NodeMetadata | None:
        """Convert raw node dict to NodeMetadata."""
        try:
            node_id = str(raw_node.get("NodeId", ""))
            if not node_id:
                return None
            
            # Convert simple integer NodeIds to OPC UA format if needed
            # Keep as-is for now - will map during normalization
            
            return NodeMetadata(
                node_id=node_id,
                tag=raw_node.get("Name", node_id),
                display_name=raw_node.get("Name"),
                data_type=raw_node.get("DataType", "Unknown"),
                description=raw_node.get("Description"),
                source_file="nodes_file"
            )
        except Exception as e:
            print(f"Error parsing node: {e}")
            return None
