"""Node metadata models."""
from typing import Optional
from pydantic import BaseModel, Field


class NodeMetadata(BaseModel):
    """Normalized node metadata from OPC UA or configuration."""
    
    node_id: str = Field(..., description="OPC UA node ID (e.g., 'ns=2;i=2')")
    tag: str = Field(..., description="Human-readable tag name (e.g., 'Temperature')")
    display_name: Optional[str] = Field(None, description="Display name from OPC UA")
    browse_name: Optional[str] = Field(None, description="Browse name from OPC UA")
    data_type: str = Field(default="Unknown", description="Data type (Float, Int32, String, Boolean, etc.)")
    unit: Optional[str] = Field(None, description="Engineering unit (°C, bar, RPM, etc.)")
    description: Optional[str] = Field(None, description="Node description")
    component: Optional[str] = Field(None, description="Component hierarchy (e.g., 'Boiler', 'Motor')")
    access_level: Optional[str] = Field(None, description="Access level (Read/Write)")
    source_file: Optional[str] = Field(None, description="Source file (machine_data, boiler_model, nodes_file)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "node_id": "ns=2;i=2",
                "tag": "Temperature",
                "display_name": "Boiler Temperature",
                "data_type": "Float",
                "unit": "°C",
                "description": "Current boiler temperature reading",
                "component": "Boiler",
                "access_level": "Read"
            }
        }


class NodeMetadataRegistry(BaseModel):
    """Registry of all node metadata indexed by node_id."""
    
    nodes: dict[str, NodeMetadata] = Field(default_factory=dict, description="Node ID -> NodeMetadata mapping")
    
    def add_node(self, metadata: NodeMetadata) -> None:
        """Add or update a node in the registry."""
        self.nodes[metadata.node_id] = metadata
    
    def get_node(self, node_id: str) -> Optional[NodeMetadata]:
        """Get node metadata by node_id."""
        return self.nodes.get(node_id)
    
    def get_by_tag(self, tag: str) -> Optional[NodeMetadata]:
        """Get node metadata by tag name."""
        for node in self.nodes.values():
            if node.tag == tag:
                return node
        return None
    
    def list_nodes(self) -> list[NodeMetadata]:
        """Return all nodes as a list."""
        return list(self.nodes.values())
    
    def list_by_component(self, component: str) -> list[NodeMetadata]:
        """Get all nodes for a specific component."""
        return [n for n in self.nodes.values() if n.component == component]
