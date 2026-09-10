"""Node resolver - maps sensor readings to node metadata."""
from typing import Optional

from app.models.reading import MachineReading, MachineDataCollection
from app.models.node import NodeMetadata, NodeMetadataRegistry


class NodeResolver:
    """Resolves sensor readings to enriched readings with metadata."""
    
    def __init__(self, registry: NodeMetadataRegistry):
        """
        Initialize resolver with node metadata registry.
        
        Args:
            registry: NodeMetadataRegistry with all node definitions
        """
        self.registry = registry
        self._unknown_nodes = set()  # Track unknown nodes
    
    def resolve_reading(self, reading: MachineReading) -> MachineReading:
        """
        Enrich a raw reading with metadata.
        
        Args:
            reading: Raw MachineReading
            
        Returns:
            Enriched MachineReading with unit, component, etc.
        """
        metadata = self._find_metadata(reading)
        
        if metadata:
            reading.unit = metadata.unit
        else:
            if reading.node_id not in self._unknown_nodes:
                print(f"WARNING: Unknown node {reading.node_id} / {reading.tag}")
                self._unknown_nodes.add(reading.node_id)
        
        return reading
    
    def resolve_collection(self, collection: MachineDataCollection) -> MachineDataCollection:
        """
        Enrich all readings in a collection.
        
        Args:
            collection: MachineDataCollection with raw readings
            
        Returns:
            Collection with enriched readings
        """
        for reading in collection.readings:
            self.resolve_reading(reading)
        
        return collection
    
    def _find_metadata(self, reading: MachineReading) -> Optional[NodeMetadata]:
        """
        Find metadata for a reading using multiple strategies.
        
        Tries in order:
        1. By node_id (primary)
        2. By tag name
        3. By node_id + tag combination
        """
        # Strategy 1: Direct node_id lookup
        metadata = self.registry.get_node(reading.node_id)
        if metadata:
            return metadata
        
        # Strategy 2: By tag name
        if reading.tag:
            metadata = self.registry.get_by_tag(reading.tag)
            if metadata:
                return metadata
        
        # Strategy 3: Partial node_id match (for cases where namespace differs)
        # e.g., "ns=2;i=2" vs "2" or "i=2"
        for node in self.registry.list_nodes():
            if self._nodes_match(reading.node_id, node.node_id):
                return node
        
        return None
    
    def _nodes_match(self, node_id1: str, node_id2: str) -> bool:
        """Check if two node ID formats refer to the same node."""
        # Extract the identifier part
        def extract_id(node_id: str) -> str:
            if ';i=' in node_id:
                return node_id.split(';i=')[1]
            elif ';s=' in node_id:
                return node_id.split(';s=')[1]
            else:
                return node_id
        
        return extract_id(node_id1) == extract_id(node_id2)
    
    def get_unknown_nodes(self) -> list[str]:
        """Get list of node_ids that were not found in metadata."""
        return list(self._unknown_nodes)
    
    def validate_registry(self, collection: MachineDataCollection) -> dict:
        """
        Validate that all nodes in collection are in registry.
        
        Args:
            collection: MachineDataCollection to validate
            
        Returns:
            Dict with validation results
        """
        unique_nodes = set()
        resolved = 0
        unresolved = 0
        
        for reading in collection.readings:
            if reading.node_id not in unique_nodes:
                unique_nodes.add(reading.node_id)
                if self._find_metadata(reading):
                    resolved += 1
                else:
                    unresolved += 1
        
        return {
            "total_unique_nodes": len(unique_nodes),
            "resolved": resolved,
            "unresolved": unresolved,
            "coverage": resolved / len(unique_nodes) if unique_nodes else 0
        }
