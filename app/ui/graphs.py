"""Graphs panel for machine variables."""
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.dates import DateFormatter
import matplotlib.dates as mdates
from datetime import datetime
from app.models.reading import MachineDataCollection


class GraphPanel(ttk.Frame):
    """Panel displaying graphs for all machine variables."""
    
    def __init__(self, parent, engine, collection: MachineDataCollection = None):
        """
        Initialize graph panel.
        
        Args:
            parent: Parent widget
            engine: MachineContextEngine instance
        """
        super().__init__(parent)
        self.engine = engine
        
        self.collection = collection
        
        self.create_graphs()
    
    def create_graphs(self):
        """Create graphs for all variables."""
        # Create canvas container
        canvas_frame = ttk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Get unique tags
        tags = set()
        for reading in self.collection.readings:
            tags.add(reading.tag)
        
        tags = sorted(list(tags))
        
        # Create figure with subplots
        num_cols = 3
        num_rows = (len(tags) + num_cols - 1) // num_cols
        
        fig = Figure(figsize=(15, 3.8 * num_rows), dpi=100, facecolor='#1e1e1e')
        fig.patch.set_facecolor('#1e1e1e')
        
        axes = fig.subplots(num_rows, num_cols)
        if num_rows == 1:
            axes = axes.reshape(1, -1)
        
        # Plot each tag
        for idx, tag in enumerate(tags):
            row = idx // num_cols
            col = idx % num_cols
            ax = axes[row, col]
            self._plot_variable(ax, tag)
        
        # Hide unused subplots
        for idx in range(len(tags), num_rows * num_cols):
            row = idx // num_cols
            col = idx % num_cols
            axes[row, col].set_visible(False)
        
        # Proper spacing between tiles to prevent text collision
        fig.subplots_adjust(left=0.06, right=0.98, top=0.94, bottom=0.10, wspace=0.25, hspace=0.42)
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def _plot_variable(self, ax, tag):
        """Plot a single variable."""
        timestamps = []
        values = []
        is_numeric = True
        unique_values = set()
        
        for reading in self.collection.readings:
            if reading.tag == tag:
                ts = reading.timestamp
                timestamps.append(ts)
                val = reading.value
                values.append(val)
                unique_values.add(str(val))
                if not isinstance(val, (int, float)):
                    is_numeric = False
        
        if not values:
            ax.text(0.5, 0.5, f"No data for {tag}", ha='center', va='center', color='white')
            ax.set_title(tag, color='white', fontweight='bold', fontsize=11)
            return

        ax.set_facecolor('#242424')
        ax.grid(True, linestyle='--', alpha=0.25, color='#777777')
        
        # Categorical variable (MachineStatus)
        if not is_numeric:
            unique_vals = sorted(list(unique_values))
            value_map = {v: i for i, v in enumerate(unique_vals)}
            numeric_values = [value_map[str(v)] for v in values]
            
            # Digital step plot
            ax.step(timestamps, numeric_values, color='#00ff66', linewidth=1.8, where='post')
            ax.fill_between(timestamps, numeric_values, step='post', alpha=0.2, color='#00ff66')
            
            ax.set_yticks(range(len(unique_vals)))
            ax.set_yticklabels(unique_vals, color='white', fontsize=8)
            ax.set_title(f"{tag}  [{', '.join(unique_vals)}]", color='white', fontweight='bold', fontsize=10, pad=8)
            ax.set_ylabel("Status", color='#cccccc', fontsize=9)
        
        # Numeric variables
        else:
            ax.plot(timestamps, values, color='#00ff66', linewidth=1.5)
            ax.fill_between(timestamps, values, alpha=0.15, color='#00ff66')
            
            min_val = min(values)
            max_val = max(values)
            avg_val = sum(values) / len(values)
            
            # Stats moved to header to prevent footer collisions
            ax.set_title(f"{tag}  [Min: {min_val:.1f} | Max: {max_val:.1f} | Avg: {avg_val:.1f}]", 
                         color='white', fontweight='bold', fontsize=10, pad=8)
            ax.set_ylabel("Value", color='#cccccc', fontsize=9)

        # Improved X-axis: show all data with intelligent spacing
        if len(timestamps) > 0:
            # Determine tick frequency based on number of data points
            num_ticks = min(10, max(3, len(timestamps) // 5))
            tick_indices = [int(i * len(timestamps) / num_ticks) for i in range(num_ticks)]
            if len(timestamps) - 1 not in tick_indices:
                tick_indices.append(len(timestamps) - 1)
            
            tick_positions = [timestamps[i] for i in sorted(set(tick_indices))]
            ax.set_xticks(tick_positions)
            ax.xaxis.set_major_formatter(DateFormatter('%H:%M:%S'))
            
        ax.tick_params(axis='x', colors='white', labelsize=7, rotation=45)
        ax.tick_params(axis='y', colors='white', labelsize=8)
        
        # Ensure labels are not cut off
        ax.margins(x=0.02)