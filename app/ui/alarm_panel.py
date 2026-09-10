"""Alarm timeline panel."""
import tkinter as tk
from tkinter import ttk
from datetime import datetime


class AlarmPanel(ttk.Frame):
    """Panel displaying alarm timeline."""
    
    def __init__(self, parent, alarm_timeline, context):
        """
        Initialize alarm panel.
        
        Args:
            parent: Parent widget
            alarm_timeline: List of alarm events
            context: MachineContext object
        """
        super().__init__(parent)
        self.alarm_timeline = alarm_timeline
        self.context = context
        
        self.create_content()
    
    def create_content(self):
        """Create content."""
        # Header
        header_frame = ttk.Frame(self)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(header_frame, text=f"Alarm Timeline - Total Alarms: {len(self.alarm_timeline)}", 
                 font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        # Summary
        critical = sum(1 for a in self.alarm_timeline if a.get("severity") == "CRITICAL")
        warning = sum(1 for a in self.alarm_timeline if a.get("severity") == "WARNING")
        
        ttk.Label(header_frame, text=f"Critical: {critical} | Warning: {warning}", 
                 font=('Arial', 10)).pack(side=tk.RIGHT, padx=10)
        
        # Create text widget with scrollbar
        text_frame = ttk.Frame(self)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set,
                             bg='#1e1e1e', fg='white', font=('Courier', 10))
        scrollbar.config(command=text_widget.yview)
        text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configure tags for colors
        text_widget.tag_config("critical", foreground="#ff0000", font=('Courier', 10, 'bold'))
        text_widget.tag_config("warning", foreground="#ffff00")
        text_widget.tag_config("info", foreground="#00ff00")
        text_widget.tag_config("timestamp", foreground="#0088ff", font=('Courier', 10, 'bold'))
        text_widget.tag_config("separator", foreground="#666666")
        
        # Populate with alarms
        for alarm in self.alarm_timeline:
            timestamp = alarm.get("timestamp", "")
            tag = alarm.get("tag", "Unknown")
            value = alarm.get("value", "N/A")
            unit = alarm.get("unit", "")
            threshold = alarm.get("threshold", "N/A")
            severity = alarm.get("severity", "INFO").upper()
            message = alarm.get("message", "")
            
            # Parse timestamp
            if isinstance(timestamp, str):
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_str = dt.strftime("%H:%M:%S")
                except:
                    time_str = str(timestamp)
            else:
                time_str = timestamp.strftime("%H:%M:%S") if hasattr(timestamp, 'strftime') else str(timestamp)
            
            # Add to text widget
            text_widget.insert(tk.END, f"[{time_str}]\n", "timestamp")
            text_widget.insert(tk.END, f"{tag} : {value}{unit}\n")
            
            if severity == "CRITICAL":
                text_widget.insert(tk.END, f"[CRITICAL ALARM]\n", "critical")
            elif severity == "WARNING":
                text_widget.insert(tk.END, f"[WARNING]\n", "warning")
            else:
                text_widget.insert(tk.END, f"[INFO]\n", "info")
            
            text_widget.insert(tk.END, f"Reason: {message}\n", "info")
            text_widget.insert(tk.END, f"Threshold: {threshold}\n", "info")
            text_widget.insert(tk.END, "-" * 60 + "\n", "separator")
        
        text_widget.config(state=tk.DISABLED)  # Read-only
