"""Tkinter Dashboard UI for Machine Context Engine."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from pathlib import Path
from jinja2 import Template

from app.main import MachineContextEngine
from app.ui.graphs import GraphPanel
from app.ui.alarm_panel import AlarmPanel
from app.ui.readings_panel import ReadingsPanel
from app.ui.nlp_templates import NLP_NARRATIVE_TEMPLATE
from app.inputs.mock_fleet import BOILER_NAMES, generate_fleet
from app.context.operator_query import resolve_query
from app.context.suggest_engine import SuggestEngine, Suggestion


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
        
        # Multi-boiler support
        self.available_boilers = []
        self.selected_boiler = None
        self.boiler_contexts = {}
        self.fleet_collections = {}
        self.boiler_selector = None
        self.notebook = None
        self.suggest_engine = SuggestEngine()
        self.suggestion_popup = None
        self.suggestion_list = None
        self.suggestions = []

        # Configure style
        self.setup_style()
        
        # Create UI
        self.create_menu()
        self.create_header()
        self.create_main_layout()
        self.root.after(100, self.load_fleet_data)
        
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
        
        title_label = ttk.Label(header, text="MACHINE CONTEXT ENGINE", style='Header.TLabel')
        title_label.grid(row=0, column=0, padx=(0, 14), sticky="w")

        ttk.Label(header, text="Unit").grid(row=0, column=1, padx=4)
        self.boiler_selector = ttk.Combobox(header, values=BOILER_NAMES, state="readonly", width=14)
        self.boiler_selector.set(BOILER_NAMES[0])
        self.boiler_selector.bind("<<ComboboxSelected>>", self.on_boiler_selected)
        self.boiler_selector.grid(row=0, column=2, padx=4)

        self.query_entry = ttk.Entry(header)
        self.query_entry.insert(0, "Ask about any boiler...")
        self.query_entry.grid(row=0, column=3, padx=(16, 4), sticky="ew")
        self.query_entry.bind("<KeyRelease>", self.on_query_key_release)
        self.query_entry.bind("<Return>", self.on_query_return)
        self.query_entry.bind("<Down>", self.on_suggestion_down)
        self.query_entry.bind("<Up>", self.on_suggestion_up)
        self.query_entry.bind("<Escape>", self.hide_suggestions)
        self.query_entry.bind("<FocusOut>", lambda _event: self.root.after(120, self.hide_suggestions))
        ttk.Button(header, text="Query", command=self.submit_query).grid(row=0, column=4, padx=4)
        
        # Status
        self.status_label = ttk.Label(header, text="Status: Ready", style='Status.TLabel')
        self.status_label.grid(row=0, column=5, padx=(12, 0), sticky="e")
        
        # Load button
        header.columnconfigure(3, weight=1)

    def on_query_key_release(self, _event=None):
        """Refresh the borderless suggestion popup after each keystroke."""
        text = self.query_entry.get().strip()
        if not text or text == "Ask about any boiler...":
            self.hide_suggestions()
            return
        self.suggestions = self.suggest_engine.suggest(text)
        if not self.suggestions:
            self.hide_suggestions()
            return
        if self.suggestion_popup is None or not self.suggestion_popup.winfo_exists():
            self.suggestion_popup = tk.Toplevel(self.root)
            self.suggestion_popup.overrideredirect(True)
            self.suggestion_popup.configure(bg="#242424")
            self.suggestion_list = tk.Listbox(
                self.suggestion_popup, bg="#242424", fg="#ffffff", selectbackground="#0078d4",
                selectforeground="#ffffff", relief=tk.FLAT, borderwidth=0, font=("Courier", 10),
                activestyle="none", height=min(7, len(self.suggestions)), exportselection=False,
            )
            self.suggestion_list.pack(fill=tk.BOTH, expand=True)
            self.suggestion_list.bind("<ButtonRelease-1>", self.on_suggestion_click)
        self.suggestion_list.delete(0, tk.END)
        for suggestion in self.suggestions:
            self.suggestion_list.insert(tk.END, suggestion.display)
        self.suggestion_list.configure(height=min(7, len(self.suggestions)))
        self.suggestion_list.selection_clear(0, tk.END)
        self.suggestion_popup.geometry(
            f"{max(self.query_entry.winfo_width(), 360)}x{min(7, len(self.suggestions)) * 24}+"
            f"{self.query_entry.winfo_rootx()}+{self.query_entry.winfo_rooty() + self.query_entry.winfo_height()}"
        )
        self.suggestion_popup.deiconify()

    def on_suggestion_down(self, _event=None):
        return self._move_suggestion(1)

    def on_suggestion_up(self, _event=None):
        return self._move_suggestion(-1)

    def _move_suggestion(self, direction: int):
        if not self.suggestion_list or not self.suggestions:
            return "break"
        current = self.suggestion_list.curselection()
        index = (current[0] + direction) % len(self.suggestions) if current else (0 if direction > 0 else len(self.suggestions) - 1)
        self.suggestion_list.selection_clear(0, tk.END)
        self.suggestion_list.selection_set(index)
        self.suggestion_list.activate(index)
        return "break"

    def on_suggestion_click(self, _event=None):
        current = self.suggestion_list.curselection() if self.suggestion_list else ()
        if current:
            self.query_entry.delete(0, tk.END)
            self.query_entry.insert(0, self.suggestions[current[0]].text)
            self.hide_suggestions()
            self.submit_query()
        return "break"

    def on_query_return(self, _event=None):
        """Execute the highlighted suggestion, or the raw typed query."""
        current = self.suggestion_list.curselection() if self.suggestion_list else ()
        if current:
            self.query_entry.delete(0, tk.END)
            self.query_entry.insert(0, self.suggestions[current[0]].text)
        self.hide_suggestions()
        self.submit_query()
        return "break"

    def hide_suggestions(self, _event=None):
        if self.suggestion_popup and self.suggestion_popup.winfo_exists():
            self.suggestion_popup.destroy()
        self.suggestion_popup = None
        self.suggestion_list = None
        return "break"
    
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
        self.hud_frame = tk.Frame(self.root, bg="#242424", highlightbackground="#0078d4", highlightthickness=1)
        self.hud_frame.pack(fill=tk.X, padx=10, pady=(0, 8))
        self.hud_label = tk.Label(
            self.hud_frame, text="Operator search results will appear here.",
            bg="#242424", fg="#d8f3dc", justify=tk.LEFT, anchor=tk.W,
            font=("Courier", 10), padx=12, pady=8,
        )
        self.hud_label.pack(fill=tk.X)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Graphs
        self.graph_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.graph_frame, text="Real-Time Graphs")
        
        # Tab 2: Readings
        self.readings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.readings_frame, text="Current Readings")
        
        # Tab 3: Alarms
        self.alarm_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.alarm_frame, text="Alarm Timeline")
        
        # Tab 4: Health
        self.health_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.health_frame, text="Health Status")

        self.response_label = tk.Text(self.root, height=5, wrap=tk.WORD, bg="#242424", fg="#d8f3dc", relief=tk.FLAT)
        self.response_label.pack(fill=tk.X, padx=10, pady=(0, 8))
        self.response_label.insert(tk.END, "Operator response: Fleet telemetry is loading...")
        self.response_label.config(state=tk.DISABLED)

    def load_fleet_data(self):
        """Load standalone telemetry and build context for each boiler."""
        self.status_label.config(text="Status: Connecting to plant telemetry...")
        self.fleet_collections = generate_fleet()
        self.engine = MachineContextEngine(config_file="config.yaml", node_metadata_json="nodesfile.json", node_metadata_xml="BoilerModel2.NodeSet2 (1).xml")
        self.boiler_contexts = {
            name: self.engine.process_collection(collection, name)
            for name, collection in self.fleet_collections.items()
        }
        self.selected_boiler = self.boiler_selector.get()
        self.context = self.boiler_contexts[self.selected_boiler]
        self.alarm_timeline = self._extract_alarm_timeline()
        self.update_all_tabs()
        self.status_label.config(text="Status: Plant telemetry online")

    def on_boiler_selected(self, _event=None):
        """Refresh every view when the operator changes unit."""
        selected = self.boiler_selector.get()
        if selected in self.boiler_contexts:
            self.selected_boiler = selected
            self.context = self.boiler_contexts[selected]
            self.alarm_timeline = self._extract_alarm_timeline()
            self.update_all_tabs()

    def submit_query(self):
        """Resolve a query, synchronize the UI, and show the shift narrative."""
        text = self.query_entry.get().strip()
        if not text or text == "Ask about any boiler..." or not self.boiler_contexts:
            return
        query = resolve_query(text, self.selected_boiler or BOILER_NAMES[0])
        if query.machine != "ALL":
            self.boiler_selector.set(query.machine)
            self.on_boiler_selected()
        if query.intent == "alarms":
            self.notebook.select(self.alarm_frame)
        elif query.intent == "health":
            self.notebook.select(self.health_frame)
        elif query.intent == "telemetry":
            self.notebook.select(self.readings_frame)
        report = self._generate_nlp_summary()
        if query.machine == "ALL":
            report = "PLANT FLEET SNAPSHOT\n\n" + "\n".join(
                f"{name}: {context.machine_state}, health {context.health_score:.0f}/100, "
                f"{context.active_alarm_count} active alarm(s)"
                for name, context in self.boiler_contexts.items()
            )
        self.response_label.config(state=tk.NORMAL)
        self.response_label.delete("1.0", tk.END)
        self.response_label.insert(tk.END, report)
        self.response_label.config(state=tk.DISABLED)
        self._update_search_hud(text)

    def _update_search_hud(self, query_text: str) -> None:
        """Render a compact metric badge, narrative, and warning state."""
        metric_aliases = {
            "temp": "Temperature", "temperature": "Temperature", "heat": "Temperature",
            "pressure": "Pressure", "bar": "Pressure", "current": "MotorCurrent",
            "amps": "MotorCurrent", "motor current": "MotorCurrent", "speed": "MotorSpeed",
            "rpm": "MotorSpeed", "motor speed": "MotorSpeed", "vibration": "Vibration",
            "status": "MachineStatus", "state": "MachineStatus",
        }
        normalized = query_text.lower()
        metric = next((tag for alias, tag in metric_aliases.items() if alias in normalized), None)
        warning = ""
        if metric and metric in self.context.current_readings:
            reading = self.context.current_readings[metric]
            stats = self.context.statistics.get(metric, {})
            warning = " | WARNING: active threshold alarm" if any(a.get("tag") == metric for a in self.context.active_alarms) else ""
            headline = (
                f"{metric}: {reading.get('value')} {reading.get('unit', '')}  |  "
                f"range {stats.get('min', 'n/a')} - {stats.get('max', 'n/a')}  |  trend {reading.get('trend', 'UNKNOWN')}"
            )
            narrative = f"{self.context.machine_name} is {self.context.machine_state.lower()}; {metric} is currently {reading.get('trend', 'stable').lower()}."
        else:
            headline = f"{self.context.machine_name}: {self.context.machine_state} | health {self.context.health_score:.0f}/100"
            narrative = self.context.summary
            warning = " | WARNING: active alarms" if self.context.active_alarms else ""
        self.hud_label.config(text=f"SEARCH RESULT  |  {headline}{warning}\n{narrative}", fg="#ffff00" if warning else "#d8f3dc")
        
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
        
        graph_panel = GraphPanel(self.graph_frame, self.engine, self.fleet_collections.get(self.selected_boiler))
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

        ttk.Label(container, text="Directional Trends:", font=('Arial', 12, 'bold')).pack(anchor=tk.W, pady=(20, 10))
        for tag, trend in self.context.trends.items():
            if trend != "UNKNOWN":
                ttk.Label(container, text=f"  {tag}: {trend}", font=('Arial', 10)).pack(anchor=tk.W)
    
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
