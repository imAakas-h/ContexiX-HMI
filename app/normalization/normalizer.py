"""Data normalization layer - combines data from multiple sources."""
from typing import Optional

from app.models.node import NodeMetadata, NodeMetadataRegistry
from app.models.reading import MachineDataCollection, MachineReading
from app.inputs.json_adapter import JSONDataAdapter, JSONMetadataAdapter
from app.inputs.xml_adapter import XMLMetadataAdapter


class DataNormalizer:
    """Normalizes machine data and metadata from heterogeneous sources."""
    
    def __init__(self):
        """Initialize normalizer."""
        self.json_data_adapter = JSONDataAdapter()
        self.json_metadata_adapter = JSONMetadataAdapter()
        self.xml_metadata_adapter = XMLMetadataAdapter()
        self.master_registry: NodeMetadataRegistry = NodeMetadataRegistry()
    
    def load_machine_data(self, json_file: str) -> MachineDataCollection:
        """
        Load and normalize machine telemetry data.
        
        Args:
            json_file: Path to machine_data_5min.json
            
        Returns:
            Normalized MachineDataCollection
        """
        collection = self.json_data_adapter.parse_collection(json_file)
        
        # Enrich readings with metadata
        for reading in collection.readings:
            metadata = self.master_registry.get_node(reading.node_id)
            if metadata:
                reading.unit = metadata.unit
        
        return collection
    
    def load_node_metadata(
        self,
        json_file: Optional[str] = None,
        xml_file: Optional[str] = None
    ) -> NodeMetadataRegistry:
        """
        Load and merge node metadata from multiple sources.
        
        Priority (later sources override earlier):
        1. JSON metadata file (nodesfile.json)
        2. XML OPC UA definitions (BoilerModel2.NodeSet2.xml)
        
        Args:
            json_file: Path to nodesfile.json (optional)
            xml_file: Path to BoilerModel2.NodeSet2.xml (optional)
            
        Returns:
            Merged NodeMetadataRegistry
        """
        registry = NodeMetadataRegistry()
        
        # Load JSON metadata first
        if json_file:
            json_registry = self.json_metadata_adapter.parse_metadata(json_file)
            for node in json_registry.list_nodes():
                registry.add_node(node)
        
        # Load XML metadata and override/enrich
        if xml_file:
            xml_registry = self.xml_metadata_adapter.parse_metadata(xml_file)
            for node in xml_registry.list_nodes():
                # Try to match by tag name or display_name
                existing = self._find_matching_node(registry, node)
                if existing:
                    # Merge: XML data takes precedence for structured fields
                    merged = self._merge_metadata(existing, node)
                    registry.add_node(merged)
                else:
                    # New node from XML
                    registry.add_node(node)
        
        # Store as master registry for enrichment
        self.master_registry = registry
        return registry
    
    def _find_matching_node(
        self,
        registry: NodeMetadataRegistry,
        new_node: NodeMetadata
    ) -> Optional[NodeMetadata]:
        """Try to find existing node by node_id, tag, or display_name."""
        # Try node_id first
        existing = registry.get_node(new_node.node_id)
        if existing:
            return existing
        
        # Try tag name
        if new_node.tag:
            existing = registry.get_by_tag(new_node.tag)
            if existing:
                return existing
        
        # Try display_name
        if new_node.display_name:
            for node in registry.list_nodes():
                if node.display_name == new_node.display_name:
                    return node
        
        return None
    
    def _merge_metadata(
        self,
        existing: NodeMetadata,
        new_node: NodeMetadata
    ) -> NodeMetadata:
        """Merge two metadata records, with new_node taking precedence."""
        return NodeMetadata(
            node_id=new_node.node_id or existing.node_id,
            tag=new_node.tag or existing.tag,
            display_name=new_node.display_name or existing.display_name,
            browse_name=new_node.browse_name or existing.browse_name,
            data_type=new_node.data_type if new_node.data_type != "Unknown" else existing.data_type,
            unit=new_node.unit or existing.unit,
            description=new_node.description or existing.description,
            component=new_node.component or existing.component,
            access_level=new_node.access_level or existing.access_level,
            source_file=f"{existing.source_file},{new_node.source_file}"
        )
    
    def enrich_with_config(
        self,
        registry: NodeMetadataRegistry,
        config: dict
    ) -> NodeMetadataRegistry:
        """
        Enrich node metadata with configuration values.
        
        Args:
            registry: Existing registry
            config: Configuration dict with node overrides
            
        Returns:
            Enriched NodeMetadataRegistry
        """
        # Config format example:
        # {
        #   "ns=2;i=2": {"unit": "°C", "component": "Boiler"},
        #   "ns=2;i=3": {"unit": "bar", "component": "Boiler"}
        # }
        
        for node_id, overrides in config.items():
            node = registry.get_node(node_id)
            
            if node:
                # Apply overrides to existing node
                if "unit" in overrides:
                    node.unit = overrides["unit"]
                if "component" in overrides:
                    node.component = overrides["component"]
                if "description" in overrides:
                    node.description = overrides["description"]
            else:
                # Create new node from config
                new_node = NodeMetadata(
                    node_id=node_id,
                    tag=overrides.get("tag", node_id),
                    unit=overrides.get("unit"),
                    component=overrides.get("component"),
                    description=overrides.get("description"),
                    source_file="config"
                )
                registry.add_node(new_node)
        
        return registry
