"""Current readings panel."""
import tkinter as tk
from tkinter import ttk


class ReadingsPanel(ttk.Frame):
    """Panel displaying current readings."""
    
    def __init__(self, parent, context):
        """
        Initialize readings panel.
        
        Args:
            parent: Parent widget
            context: MachineContext object
        """
        super().__init__(parent)
        self.context = context
        
        self.create_content()
    
    def create_content(self):
        """Create content."""
        # Header
        header = ttk.Label(self, text="Current Machine Readings", font=('Arial', 14, 'bold'))
        header.pack(pady=10)
        
        # Create treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Treeview
        tree = ttk.Treeview(tree_frame, columns=("Value", "Unit", "Trend", "Status"), 
                           height=20, yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)
        
        # Define columns
        tree.column("#0", width=150, minwidth=150, anchor=tk.W)
        tree.column("Value", width=100, minwidth=100, anchor=tk.CENTER)
        tree.column("Unit", width=80, minwidth=80, anchor=tk.CENTER)
        tree.column("Trend", width=100, minwidth=100, anchor=tk.CENTER)
        tree.column("Status", width=100, minwidth=100, anchor=tk.CENTER)
        
        # Headings
        tree.heading("#0", text="Tag", anchor=tk.W)
        tree.heading("Value", text="Value", anchor=tk.CENTER)
        tree.heading("Unit", text="Unit", anchor=tk.CENTER)
        tree.heading("Trend", text="Trend", anchor=tk.CENTER)
        tree.heading("Status", text="Status", anchor=tk.CENTER)
        
        # Add data
        for tag, reading in self.context.current_readings.items():
            value = reading.get("value", "N/A")
            unit = reading.get("unit", "")
            trend = reading.get("trend", "UNKNOWN")
            quality = reading.get("quality", "UNKNOWN")
            
            # Format value
            if isinstance(value, float):
                value_str = f"{value:.2f}"
            else:
                value_str = str(value)
            
            # Determine status color
            if trend == "INCREASING":
                trend_str = "↗ INCREASING"
            elif trend == "DECREASING":
                trend_str = "↘ DECREASING"
            elif trend == "STABLE":
                trend_str = "→ STABLE"
            else:
                trend_str = "? UNKNOWN"
            
            tree.insert("", tk.END, text=tag, 
                       values=(value_str, unit, trend_str, quality))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Summary
        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(summary_frame, text=f"Total Readings: {len(self.context.current_readings)}", 
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
        ttk.Label(summary_frame, text=f"Communication Quality: {self.context.communication_quality:.0%}", 
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
