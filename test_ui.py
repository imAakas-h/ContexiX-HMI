#!/usr/bin/env python3
"""Quick test of the UI components."""
import sys
import io

# Fix Unicode on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Test imports
try:
    print("Testing imports...")
    from app.ui.dashboard import MCEDashboard
    from app.ui.graphs import GraphPanel
    from app.ui.readings_panel import ReadingsPanel
    from app.ui.alarm_panel import AlarmPanel
    print("[+] All UI modules imported successfully")
    
    from app.main import MachineContextEngine
    print("[+] Engine imported successfully")
    
    import tkinter as tk
    from tkinter import ttk
    print("[+] Tkinter imported successfully")
    
    import matplotlib
    print("[+] Matplotlib imported successfully")
    
    print("\nAll dependencies are ready!")
    print("\nTo launch the UI, run: python launch_ui.py")
    
except ImportError as e:
    print(f"[!] Import error: {e}")
    print("\nInstalling missing dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
