"""XML adapter for reading OPC UA NodeSet definitions."""
import xml.etree.ElementTree as ET
from typing import Any, Optional

from app.models.node import NodeMetadata, NodeMetadataRegistry


class XMLMetadataAdapter:
    """Reads OPC UA NodeSet2 XML format (BoilerModel2.NodeSet2.xml)."""
    
    def __init__(self):
        """Initialize XML adapter."""
        self.ns = {
            'ua': 'http://opcfoundation.org/UA/2011/03/UANodeSet.xsd'
        }
    
    def read(self, source: str) -> ET.Element:
        """Read and parse XML file."""
        tree = ET.parse(source)
        return tree.getroot()
    
    def parse_metadata(self, source: str) -> NodeMetadataRegistry:
        """Parse OPC UA NodeSet XML into NodeMetadataRegistry."""
        root = self.read(source)
        registry = NodeMetadataRegistry()
        
        # Parse UAVariables (sensor values)
        for var in root.findall('.//ua:UAVariable', self.ns):
            metadata = self._parse_ua_variable(var)
            if metadata:
                registry.add_node(metadata)
        
        # Parse UAObjects (components)
        for obj in root.findall('.//ua:UAObject', self.ns):
            metadata = self._parse_ua_object(obj)
            if metadata:
                registry.add_node(metadata)
        
        return registry
    
    def _parse_ua_variable(self, element: ET.Element) -> NodeMetadata | None:
        """Convert UAVariable XML element to NodeMetadata."""
        try:
            node_id = element.get('NodeId', '')
            if not node_id:
                return None
            
            browse_name = element.get('BrowseName', '')
            display_name_elem = element.find('ua:DisplayName', self.ns)
            display_name = display_name_elem.text if display_name_elem is not None else None
            
            data_type = element.get('DataType', 'Unknown')
            
            # Extract description from DisplayName or References
            description = None
            
            return NodeMetadata(
                node_id=node_id,
                tag=display_name or browse_name or node_id,
                display_name=display_name,
                browse_name=browse_name,
                data_type=data_type,
                description=description,
                access_level=element.get('AccessLevel'),
                source_file="boiler_model"
            )
        except Exception as e:
            print(f"Error parsing UAVariable: {e}")
            return None
    
    def _parse_ua_object(self, element: ET.Element) -> NodeMetadata | None:
        """Convert UAObject XML element to NodeMetadata."""
        try:
            node_id = element.get('NodeId', '')
            if not node_id:
                return None
            
            browse_name = element.get('BrowseName', '')
            display_name_elem = element.find('ua:DisplayName', self.ns)
            display_name = display_name_elem.text if display_name_elem is not None else None
            
            # Try to extract component from references
            component = None
            
            return NodeMetadata(
                node_id=node_id,
                tag=display_name or browse_name or node_id,
                display_name=display_name,
                browse_name=browse_name,
                data_type="Object",
                component=component,
                source_file="boiler_model"
            )
        except Exception as e:
            print(f"Error parsing UAObject: {e}")
            return None
    
    def extract_hierarchy(self, source: str) -> dict[str, list[str]]:
        """Extract component hierarchy from HasComponent references."""
        root = self.read(source)
        hierarchy = {}
        
        # For each UAObject, find its components
        for obj in root.findall('.//ua:UAObject', self.ns):
            node_id = obj.get('NodeId')
            if not node_id:
                continue
            
            components = []
            refs = obj.find('ua:References', self.ns)
            if refs is not None:
                for ref in refs.findall('ua:Reference', self.ns):
                    if 'HasComponent' in ref.get('ReferenceType', ''):
                        target = ref.text
                        if target:
                            components.append(target)
            
            if components:
                hierarchy[node_id] = components
        
        return hierarchy
