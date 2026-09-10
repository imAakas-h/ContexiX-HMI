"""Tkinter Dashboard UI for Machine Context Engine."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
from pathlib import Path
from jinja2 import Environment, Template

from app.main import MachineContextEngine
from app.ui.graphs import GraphPanel
from app.ui.alarm_panel import AlarmPanel
from app.ui.readings_panel import ReadingsPanel
from app.ui.nlp_templates import NLP_NARRATIVE_TEMPLATE


class MCEDashboard:
    """Main dashboard application."""
    
    def __init__(self, root):
        """Initialize dashboard."""
        self.root = root
        self.root.title("Machine Context Engine - Dashboard")
        self.root.geometry("1600x900")
        
        self.engine = None
        self.context = None
        self.alarm_timeline = []
        self.selected_files = {
            'machine_data': None,
            'node_metadata': None,
            'node_xml': None,
            'config': None
        }
        
        # Configure style
        self.setup_style()
        
        # Create UI
        self.create_menu()
        self.create_header()
        self.create_file_selector()
        self.create_main_layout()
        
    def setup_style(self):
        """Setup ttk style."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Colors
        bg_color = "#1e1e1e"
        fg_color = "#ffffff"
        accent_color = "#0078d4"
        
        style.configure('TFrame', background=bg_color)
        style.configure('TLabel', background=bg_color, foreground=fg_color)
        style.configure('TButton', background=accent_color, foreground=fg_color)
        style.configure('Header.TLabel', background="#2d2d2d", foreground=fg_color, font=('Arial', 12, 'bold'))
        style.configure('Status.TLabel', background=bg_color, foreground="#00ff00", font=('Arial', 10))
        
        self.root.configure(bg=bg_color)
    
    def create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Upload Machine Data", command=self.select_machine_data)
        file_menu.add_command(label="Upload Node Metadata", command=self.select_node_metadata)
        file_menu.add_command(label="Upload Node XML", command=self.select_node_xml)
        file_menu.add_command(label="Upload Config", command=self.select_config)
        file_menu.add_separator()
        file_menu.add_command(label="Load & Process", command=self.load_data)
        file_menu.add_separator()
        file_menu.add_command(label="Export NLP Summary", command=self.export_nlp_summary)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def create_header(self):
        """Create header section."""
        header = ttk.Frame(self.root)
        header.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = ttk.Label(header, text="⚙ MACHINE CONTEXT ENGINE", style='Header.TLabel')
        title_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Status
        self.status_label = ttk.Label(header, text="Status: Ready", style='Status.TLabel')
        self.status_label.pack(side=tk.RIGHT)
        
        # Load button
        load_btn = ttk.Button(header, text="Load & Process", command=self.load_data)
        load_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_file_selector(self):
        """Create file selector section."""
        file_frame = ttk.LabelFrame(self.root, text="Upload Your Files", padding=10)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Row 1: Machine Data
        row1 = ttk.Frame(file_frame)
        row1.pack(fill=tk.X, pady=5)
        ttk.Button(row1, text="Machine Data (JSON)", command=self.select_machine_data, width=20).pack(side=tk.LEFT, padx=5)
        self.machine_data_label = ttk.Label(row1, text="No file selected", foreground="gray")
        self.machine_data_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Row 2: Node Metadata
        row2 = ttk.Frame(file_frame)
        row2.pack(fill=tk.X, pady=5)
        ttk.Button(row2, text="Node Metadata (JSON)", command=self.select_node_metadata, width=20).pack(side=tk.LEFT, padx=5)
        self.node_metadata_label = ttk.Label(row2, text="No file selected", foreground="gray")
        self.node_metadata_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Row 3: Node XML
        row3 = ttk.Frame(file_frame)
        row3.pack(fill=tk.X, pady=5)
        ttk.Button(row3, text="Node XML Definitions", command=self.select_node_xml, width=20).pack(side=tk.LEFT, padx=5)
        self.node_xml_label = ttk.Label(row3, text="No file selected", foreground="gray")
        self.node_xml_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Row 4: Config
        row4 = ttk.Frame(file_frame)
        row4.pack(fill=tk.X, pady=5)
        ttk.Button(row4, text="Config (YAML)", command=self.select_config, width=20).pack(side=tk.LEFT, padx=5)
        self.config_label = ttk.Label(row4, text="No file selected", foreground="gray")
        self.config_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def select_machine_data(self):
        """Select machine data file."""
        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file:
            self.selected_files['machine_data'] = file
            self.machine_data_label.config(text=Path(file).name, foreground="green")
    
    def select_node_metadata(self):
        """Select node metadata file."""
        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if file:
            self.selected_files['node_metadata'] = file
            self.node_metadata_label.config(text=Path(file).name, foreground="green")
    
    def select_node_xml(self):
        """Select node XML file."""
        file = filedialog.askopenfilename(filetypes=[("XML files", "*.xml"), ("All files", "*.*")])
        if file:
            self.selected_files['node_xml'] = file
            self.node_xml_label.config(text=Path(file).name, foreground="green")
    
    def select_config(self):
        """Select config file."""
        file = filedialog.askopenfilename(filetypes=[("YAML files", "*.yaml"), ("All files", "*.*")])
        if file:
            self.selected_files['config'] = file
            self.config_label.config(text=Path(file).name, foreground="green")
    
    def create_main_layout(self):
        """Create main layout with tabs."""
        # Create notebook (tabs)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Graphs
        self.graph_frame = ttk.Frame(notebook)
        notebook.add(self.graph_frame, text="Real-Time Graphs")
        
        # Tab 2: Readings
        self.readings_frame = ttk.Frame(notebook)
        notebook.add(self.readings_frame, text="Current Readings")
        
        # Tab 3: Alarms
        self.alarm_frame = ttk.Frame(notebook)
        notebook.add(self.alarm_frame, text="Alarm Timeline")
        
        # Tab 4: Health
        self.health_frame = ttk.Frame(notebook)
        notebook.add(self.health_frame, text="Health Status")
        
    def load_data(self):
        """Load and process machine data."""
        # Check if files are selected
        if not self.selected_files['machine_data']:
            messagebox.showwarning("Warning", "Please select Machine Data file first")
            return
        
        self.status_label.config(text="Status: Processing...")
        self.root.update()
        
        try:
            # Get file paths
            machine_data_file = self.selected_files['machine_data']
            node_metadata_file = self.selected_files['node_metadata'] or "nodesfile.json"
            node_xml_file = self.selected_files['node_xml'] or "BoilerModel2.NodeSet2 (1).xml"
            config_file = self.selected_files['config'] or "config.yaml"
            
            # Initialize engine
            self.engine = MachineContextEngine(
                config_file=config_file if Path(config_file).exists() else None,
                node_metadata_json=node_metadata_file if Path(node_metadata_file).exists() else None,
                node_metadata_xml=node_xml_file if Path(node_xml_file).exists() else None
            )
            
            # Process data
            self.context = self.engine.process(machine_data_file)
            
            # Extract alarm timeline
            self.alarm_timeline = self._extract_alarm_timeline()
            
            # Update UI
            self.update_all_tabs()
            
            self.status_label.config(text=f"Status: Ready | Alarms: {len(self.alarm_timeline)}")
            messagebox.showinfo("Success", f"Data loaded successfully!\nAlarms detected: {len(self.alarm_timeline)}")
            
        except Exception as e:
            self.status_label.config(text=f"Status: Error - {str(e)}")
            messagebox.showerror("Error", f"Failed to load data: {str(e)}")
    
    def update_all_tabs(self):
        """Update all tab content."""
        self.update_graphs_tab()
        self.update_readings_tab()
        self.update_alarm_tab()
        self.update_health_tab()
    
    def update_graphs_tab(self):
        """Update graphs tab."""
        # Clear previous content
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        if not self.context:
            return
        
        graph_panel = GraphPanel(self.graph_frame, self.engine)
        graph_panel.pack(fill=tk.BOTH, expand=True)
    
    def update_readings_tab(self):
        """Update readings tab."""
        # Clear previous content
        for widget in self.readings_frame.winfo_children():
            widget.destroy()
        
        if not self.context:
            return
        
        readings_panel = ReadingsPanel(self.readings_frame, self.context)
        readings_panel.pack(fill=tk.BOTH, expand=True)
    
    def update_alarm_tab(self):
        """Update alarm tab."""
        # Clear previous content
        for widget in self.alarm_frame.winfo_children():
            widget.destroy()
        
        if not self.alarm_timeline:
            label = ttk.Label(self.alarm_frame, text="No alarms detected")
            label.pack(pady=20)
            return
        
        alarm_panel = AlarmPanel(self.alarm_frame, self.alarm_timeline, self.context)
        alarm_panel.pack(fill=tk.BOTH, expand=True)
    
    def update_health_tab(self):
        """Update health tab."""
        # Clear previous content
        for widget in self.health_frame.winfo_children():
            widget.destroy()
        
        if not self.context:
            return
        
        self._create_health_display(self.health_frame)
    
    def _create_health_display(self, parent):
        """Create health display."""
        # Main container
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Health score
        score_frame = ttk.Frame(container)
        score_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(score_frame, text=f"Health Score:", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        ttk.Label(score_frame, text=f"{self.context.health_score:.0f}/100", font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=10)
        ttk.Label(score_frame, text=f"Status: {self.context.health_status}", font=('Arial', 14, 'bold')).pack(side=tk.LEFT, padx=10)
        
        # Machine state
        state_frame = ttk.Frame(container)
        state_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(state_frame, text=f"Machine State:", font=('Arial', 12)).pack(side=tk.LEFT)
        ttk.Label(state_frame, text=f"{self.context.machine_state}", font=('Arial', 12, 'bold')).pack(side=tk.LEFT, padx=10)
        
        # Health reasons
        ttk.Label(container, text="Health Factors:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(20, 10))
        
        for reason in self.context.health_reasons:
            ttk.Label(container, text=f"  • {reason}", font=('Arial', 10)).pack(anchor=tk.W)
        
        # Active alarms
        ttk.Label(container, text=f"Active Alarms: {len(self.context.active_alarms)}", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(20, 10))
        
        # Anomalies
        ttk.Label(container, text=f"Anomalies Detected: {len(self.context.anomalies)}", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(20, 10))
    
    def _extract_alarm_timeline(self) -> list:
        """Extract alarm timeline."""
        timeline = []
        for alarm in self.context.active_alarms:
            timeline.append({
                "timestamp": alarm.get("timestamp"),
                "tag": alarm.get("tag"),
                "value": alarm.get("value"),
                "unit": self.context.current_readings.get(alarm.get("tag"), {}).get("unit", ""),
                "threshold": alarm.get("threshold"),
                "severity": alarm.get("severity"),
                "message": alarm.get("message")
            })
        timeline.sort(key=lambda x: x.get("timestamp", ""))
        return timeline
    
    def show_about(self):
        """Show about dialog."""
        messagebox.showinfo("About", "Machine Context Engine v1.0\n\nOffline OPC-UA Data Analysis Tool")
    
    def export_nlp_summary(self):
        """Export NLP-ready summary."""
        if not self.context:
            messagebox.showwarning("Warning", "Please load data first")
            return
        
        # Generate NLP summary
        nlp_summary = self._generate_nlp_summary()
        
        # Ask user where to save
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            initialfile="nlp_summary.txt"
        )
        
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(nlp_summary)
            messagebox.showinfo("Success", f"NLP summary exported to:\n{file_path}")
    
    def _generate_nlp_summary(self) -> str:
        """Generate dynamic story-based NLP summary using Jinja2 templates."""
        # Prepare data context for Jinja2
        context_data = {
            'health_score': self.context.health_score,
            'health_status': self.context.health_status,
            'machine_state': self.context.machine_state,
            'state_duration_seconds': self.context.state_duration_seconds,
            'current_readings': self.context.current_readings,
            'health_reasons': self.context.health_reasons,
            'active_alarms': self.context.active_alarms,
            'trends': self.context.trends,
            'statistics': self.context.statistics,
            'anomalies': self.context.anomalies,
            'generated_at': datetime.now().isoformat()
        }
        
        # Render template with context
        template = Template(NLP_NARRATIVE_TEMPLATE)
        summary = template.render(context_data)
        
        return summary


def run_dashboard():
    """Run the dashboard application."""
    root = tk.Tk()
    app = MCEDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    run_dashboard()
