"""Base adapter interface for input sources."""
from abc import ABC, abstractmethod
from typing import Any
from app.models.reading import MachineDataCollection
from app.models.node import NodeMetadata, NodeMetadataRegistry


class BaseAdapter(ABC):
    """Base adapter for reading machine data or metadata."""
    
    @abstractmethod
    def read(self, source: str) -> Any:
        """
        Read data from source.
        
        Args:
            source: File path or connection string
            
        Returns:
            Parsed data as appropriate type
        """
        pass


class DataAdapter(BaseAdapter):
    """Adapter for reading machine telemetry data."""
    
    @abstractmethod
    def parse_collection(self, source: str) -> MachineDataCollection:
        """Parse machine data into normalized MachineDataCollection."""
        pass


class MetadataAdapter(BaseAdapter):
    """Adapter for reading node metadata."""
    
    @abstractmethod
    def parse_metadata(self, source: str) -> NodeMetadataRegistry:
        """Parse node metadata into NodeMetadataRegistry."""
        pass
