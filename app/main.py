"""Machine Context Engine - Main orchestrator."""
from pathlib import Path
from typing import Optional

from app.config import Config
from app.models.context import MachineContext
from app.models.reading import MachineDataCollection
from app.models.node import NodeMetadataRegistry
from app.normalization.normalizer import DataNormalizer
from app.resolver.node_resolver import NodeResolver
from app.context.builder import ContextBuilder
from app.context.llm_context import LLMContextGenerator


class MachineContextEngine:
    """
    Main Machine Context Engine.
    
    Orchestrates the complete pipeline:
    1. Load input files (JSON, XML)
    2. Normalize data
    3. Resolve nodes to metadata
    4. Run engines (state, alarms, trends, anomalies, health)
    5. Build machine context
    6. Generate LLM-ready output
    """
    
    def __init__(
        self,
        config_file: Optional[str] = None,
        node_metadata_json: Optional[str] = None,
        node_metadata_xml: Optional[str] = None
    ):
        """
        Initialize Machine Context Engine.
        
        Args:
            config_file: Path to config.yaml
            node_metadata_json: Path to nodesfile.json
            node_metadata_xml: Path to BoilerModel2.NodeSet2.xml
        """
        # Load configuration
        self.config = Config(config_file)
        
        # Initialize normalizer
        self.normalizer = DataNormalizer()
        
        # Load node metadata
        self.node_registry = self.normalizer.load_node_metadata(
            json_file=node_metadata_json,
            xml_file=node_metadata_xml
        )
        
        # Enrich with config
        if config_file:
            self.node_registry = self.normalizer.enrich_with_config(
                self.node_registry,
                self.config.get("nodes", {})
            )
        
        # Initialize node resolver
        self.resolver = NodeResolver(self.node_registry)
        
        # Initialize context builder with engines
        self.context_builder = ContextBuilder(self.node_registry, config=self.config.get("engines", {}))
        
        # Initialize LLM context generator
        self.llm_generator = LLMContextGenerator()
        
        # Last processed context
        self.last_context = None
    
    def process(self, machine_data_file: str) -> MachineContext:
        """
        Process machine data and generate context.
        
        Args:
            machine_data_file: Path to machine_data_5min.json
            
        Returns:
            MachineContext with complete machine analysis
        """
        # Step 1: Load machine data
        collection = self.normalizer.load_machine_data(machine_data_file)
        
        # Step 2: Resolve nodes
        collection = self.resolver.resolve_collection(collection)
        
        # Step 3: Validate coverage
        validation = self.resolver.validate_registry(collection)
        print(f"Node resolution coverage: {validation['coverage']:.1%}")
        
        # Step 4: Build context
        context = self.context_builder.build(collection, self.config.get("machine", {}).get("name", "Machine System"))
        
        self.last_context = context
        return context

    def process_collection(self, collection: MachineDataCollection, machine_name: str) -> MachineContext:
        """Resolve and evaluate an in-memory collection for one machine."""
        collection = self.resolver.resolve_collection(collection)
        builder = ContextBuilder(self.node_registry, config=self.config.get("engines", {}))
        context = builder.build(collection, machine_name)
        self.last_context = context
        return context
    
    def get_context(self) -> Optional[MachineContext]:
        """Get the last generated context."""
        return self.last_context
    
    def get_llm_context(self) -> Optional[str]:
        """Get LLM-ready context string."""
        if self.last_context:
            return self.llm_generator.generate(self.last_context)
        return None
    
    def get_compact_context(self) -> Optional[str]:
        """Get compact context string."""
        if self.last_context:
            return self.llm_generator.generate_compact(self.last_context)
        return None
    
    def get_node_registry(self) -> NodeMetadataRegistry:
        """Get node metadata registry."""
        return self.node_registry
    
    def get_unknown_nodes(self) -> list[str]:
        """Get list of unknown nodes."""
        return self.resolver.get_unknown_nodes()
