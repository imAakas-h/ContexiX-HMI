# Machine Context Engine - Complete Documentation Index

## 🚀 Quick Start (Start Here!)

**New users:** Read these files in order:

1. **QUICKSTART.txt** ← START HERE
   - 3 simple ways to launch the system
   - Basic usage instructions
   - Troubleshooting tips

2. **DASHBOARD_GUIDE.txt** 
   - Detailed walkthrough of the UI
   - What each tab shows
   - How to interpret graphs

3. **README.md**
   - Complete feature list
   - Installation instructions
   - All available endpoints

## 📊 How to Use

### Launch Interactive Dashboard with Graphs
```bash
python launch_ui.py
```
**Best for:** Visualizing your data with graphs and exploring interactively

### Generate Professional Report
```bash
python generate_report.py
```
**Best for:** Creating formatted documentation with alarm timeline

### Start REST API Server
```bash
python run_api.py
```
**Best for:** Programmatic access and integration with other systems

## 📁 File Guide

### Documentation Files (Read These)

| File | Purpose | Audience |
|------|---------|----------|
| **QUICKSTART.txt** | Get started in 5 minutes | Everyone |
| **README.md** | Complete feature documentation | Developers |
| **DASHBOARD_GUIDE.txt** | UI walkthrough with visuals | UI users |
| **SYSTEM_SUMMARY.md** | Architecture and design | Technical leads |
| **INDEX.md** | This file - navigation | Everyone |

### Application Files (The Code)

```
app/
├── main.py                 ← Main engine class
├── config.py               ← Configuration management
├── models/                 ← Data models
│   ├── reading.py
│   ├── context.py
│   ├── event.py
│   └── node.py
├── inputs/                 ← Data adapters
│   ├── json_adapter.py
│   ├── xml_adapter.py
│   └── base_adapter.py
├── normalization/          ← Data normalization
│   └── normalizer.py
├── resolver/               ← Node resolution
│   └── node_resolver.py
├── engines/                ← Analysis engines
│   ├── machine_state.py
│   ├── alarm_engine.py
│   ├── trend_engine.py
│   ├── anomaly_engine.py
│   └── health_engine.py
├── context/                ← Context building
│   ├── builder.py
│   ├── llm_context.py
│   └── report_generator.py
├── ui/                     ← Tkinter dashboard
│   ├── dashboard.py
│   ├── graphs.py
│   ├── readings_panel.py
│   └── alarm_panel.py
└── api/                    ← REST API
    └── routes.py
```

### Data Files (Your Input)

```
├── machine_data_5min.json       ← 1,800 sensor readings (5 min)
├── nodesfile.json               ← Node metadata
├── BoilerModel2.NodeSet2.xml    ← OPC-UA boiler model
├── Opc.Ua.DI.NodeSet2.xml       ← OPC-UA device integration standard
└── config.yaml                  ← Configuration (edit this!)
```

### Launcher Scripts

```
├── launch_ui.py             ← Start dashboard
├── generate_report.py       ← Create text report
├── run_api.py               ← Start REST API
└── test_ui.py               ← Test dependencies
```

## 🎯 Use Cases

### "I want to see my data as graphs"
→ Run: `python launch_ui.py`
→ Go to: Real-Time Graphs tab
→ See all 6 variables plotted over 5 minutes

### "I want to know what alarms were triggered"
→ Run: `python launch_ui.py`
→ Go to: Alarm Timeline tab
→ See 6 alarms with exact timestamps

OR

→ Run: `python generate_report.py`
→ Open: machine_context_report.txt
→ See formatted alarm history

### "I want to integrate this with my system"
→ Run: `python run_api.py`
→ Visit: http://localhost:8000/docs
→ Call endpoints programmatically

### "I want to analyze data in Python"
```python
from app.main import MachineContextEngine

engine = MachineContextEngine(
    config_file="config.yaml",
    node_metadata_json="nodesfile.json",
    node_metadata_xml="BoilerModel2.NodeSet2 (1).xml"
)

context = engine.process("machine_data_5min.json")

print(f"State: {context.machine_state}")
print(f"Health: {context.health_score}")
print(f"Alarms: {len(context.active_alarms)}")
```

## 📈 What You'll See

### Dashboard Tabs

1. **Real-Time Graphs**
   - 6 interactive time-series plots
   - All sensor variables
   - Min/Max/Average statistics

2. **Current Readings**
   - Latest values for each sensor
   - Units and data types
   - Trend indicators

3. **Alarm Timeline**
   - All alarms chronologically
   - Exact timestamps
   - Reason for each alarm

4. **Health Status**
   - Overall health score (0-100)
   - Machine state
   - Health factors

### Report Output

```
================================================================================
MACHINE CONTEXT ENGINE (MCE)
================================================================================

[19:13:37] Pressure: 0.783 bar
[!] WARNING GENERATED
Reason: Pressure fallen below threshold (0.8)

[19:13:38] Temperature: 25.27°C
[!] WARNING GENERATED
Reason: Temperature exceeded threshold (25.0)

... (6 alarms total)

CURRENT STATE: RUNNING
HEALTH SCORE: 0/100
STATUS: CRITICAL
```

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# Machine name
machine:
  name: "Boiler System"

# Alarm thresholds
engines:
  alarm:
    thresholds:
      Temperature:
        high: 25.0
        low: 15.0
      Pressure:
        high: 1.3
        low: 0.8

# Health scoring
  health:
    thresholds:
      critical: 40
      warning: 70
      normal: 85
```

## 🔧 Customization

### Change Alarm Thresholds
Edit `config.yaml`

### Add Machine Name
```yaml
machine:
  name: "My Custom Machine Name"
```

### Adjust Units
```yaml
nodes:
  "ns=2;i=2":
    unit: "°C"
```

### Change Health Scoring
```yaml
engines:
  health:
    scoring:
      critical_alarm: -30
      warning_alarm: -15
```

## 🐛 Troubleshooting

**Issue: UI won't start**
```bash
python test_ui.py
pip install -r requirements.txt
```

**Issue: No alarms detected**
→ Check config.yaml thresholds
→ Compare with actual data range in graphs
→ Verify threshold values make sense

**Issue: Wrong units showing**
→ Update config.yaml with units
→ Format: `unit: "°C"` for Temperature

**Issue: No data in graphs**
→ Verify machine_data_5min.json exists
→ Check file format is correct JSON
→ Ensure data contains numeric values

## 📊 Data Details

### Machine Data
- **Total readings:** 1,800
- **Duration:** 5 minutes
- **Sampling:** 1 second intervals
- **Variables:** 6 (Temperature, Pressure, MotorSpeed, MotorCurrent, Vibration, MachineStatus)
- **Time range:** 2026-09-10 19:09:37 to 19:14:40

### Alarms Detected
- **Total:** 6 alarms
- **Timestamp range:** 19:13:37 to 19:14:36
- **Types:** 
  - Pressure low (0.783 bar < 0.8 threshold)
  - Temperature high (25.27°C > 25.0 threshold)
  - Motor current low (4.37 A < 4.5 threshold)
  - Temperature low (14.89°C < 15.0 threshold)
  - Vibration high (0.814 mm/s > 0.8 threshold)
  - Motor current high (6.05 A > 6.0 threshold)

## 🎓 Learning Resources

### Understand the Architecture
→ Read: SYSTEM_SUMMARY.md
→ Includes: Data flow diagram, component descriptions

### Learn the UI
→ Read: DASHBOARD_GUIDE.txt
→ Includes: Visual layout, feature descriptions

### Get Started Quickly
→ Read: QUICKSTART.txt
→ Includes: 3-step getting started

### Deep Dive
→ Read: README.md
→ Includes: All features, endpoints, customization

## 📝 API Reference

Base URL: `http://localhost:8000`

**Key Endpoints:**

| Endpoint | Method | Returns |
|----------|--------|---------|
| `/context` | GET | Complete machine context |
| `/machine/state` | GET | Current machine state |
| `/machine/health` | GET | Health status and score |
| `/alarms` | GET | Active alarms |
| `/readings` | GET | Current sensor readings |
| `/trends` | GET | Trend analysis |
| `/anomalies` | GET | Detected anomalies |
| `/nodes` | GET | Node definitions |
| `/context/llm` | GET | LLM-ready context |

**Full documentation:** http://localhost:8000/docs

## 🚦 Getting Started Steps

### Step 1: Verify Setup
```bash
python test_ui.py
```

### Step 2: Launch Dashboard
```bash
python launch_ui.py
```

### Step 3: Click "Load & Process"
In the UI window

### Step 4: Explore Tabs
- See graphs
- Check readings
- Review alarms
- View health

### Step 5: (Optional) Generate Report
```bash
python generate_report.py
```

### Step 6: (Optional) Start API
```bash
python run_api.py
```

## 📞 Support

**For detailed info, see:**
- README.md - Full documentation
- SYSTEM_SUMMARY.md - Architecture
- DASHBOARD_GUIDE.txt - UI walkthrough
- QUICKSTART.txt - Getting started

**Common issues are documented in QUICKSTART.txt troubleshooting section**

## ✨ Key Features

✅ **Real-time graphs** for all 6 variables  
✅ **Alarm detection** with exact timestamps  
✅ **Professional dashboard** UI with 4 tabs  
✅ **Trend analysis** (INCREASING/DECREASING/STABLE)  
✅ **Health scoring** with detailed reasoning  
✅ **REST API** for integration  
✅ **Report generation** with timeline  
✅ **Configuration** via YAML  
✅ **All real data** - no mock data  

## 🎯 Summary

The Machine Context Engine is a complete system for analyzing your OPC-UA machine telemetry:

1. **Input:** Your JSON machine data + XML node definitions
2. **Processing:** Normalizes data, detects alarms, calculates health
3. **Output:** Interactive dashboard, graphs, reports, API

**To get started:** `python launch_ui.py`

---

**Created:** 2026-09-10  
**Version:** 1.0.0  
**Status:** Production Ready
