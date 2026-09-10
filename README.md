# Machine Context Engine (MCE)

A comprehensive offline OPC-UA data analysis system with real-time visualization and alarm detection.

## Features

✓ **Real-time Data Processing** - Reads and normalizes machine telemetry from JSON  
✓ **Alarm Detection** - Configurable thresholds with timestamp tracking  
✓ **Time-Series Graphs** - Interactive matplotlib visualizations for all variables  
✓ **Professional Dashboard** - Tkinter-based GUI with multiple views  
✓ **Trend Analysis** - Automatic trend detection (INCREASING, DECREASING, STABLE)  
✓ **Health Scoring** - Overall machine health with detailed reasoning  
✓ **REST API** - FastAPI endpoints for integration  
✓ **Report Generation** - Professional formatted timeline reports  

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### 1. Launch the Dashboard UI

```bash
python launch_ui.py
```

This opens a Tkinter dashboard with:
- **Real-Time Graphs** - All machine variables plotted over time
- **Current Readings** - Latest values with trends and units
- **Alarm Timeline** - Complete history of detected alarms with timestamps
- **Health Status** - Overall machine health and factors

### 2. Generate Report (CLI)

```bash
python generate_report.py
```

Produces:
- `machine_context_report.txt` - Professional formatted report
- Shows alarm timeline with exact timestamps
- Lists current readings and health status
- Includes recommendations

### 3. Use REST API

```bash
# Start API server
python run_api.py

# Get context
curl http://localhost:8000/context

# Get alarms
curl http://localhost:8000/alarms

# Get trends
curl http://localhost:8000/trends
```

## Configuration

Edit `config.yaml` to customize:

```yaml
machine:
  name: "Boiler System"

nodes:
  "ns=2;i=2":
    unit: "°C"
    component: "Boiler"
    
engines:
  alarm:
    thresholds:
      Temperature:
        high: 25.0
        low: 15.0
      Pressure:
        high: 1.3
        low: 0.8
```

## Data Format

### Input: machine_data_5min.json

```json
{
  "collection_info": {
    "source": "opc.tcp://localhost:4840/mce/server/",
    "duration_seconds": 300,
    "sampling_interval_seconds": 1,
    "start_time": "2026-09-10T19:09:37.292205+00:00",
    "end_time": "2026-09-10T19:14:40.250828+00:00"
  },
  "data": [
    {
      "timestamp": "2026-09-10T19:09:37.293204+00:00",
      "node_id": "ns=2;i=2",
      "tag": "Temperature",
      "value": 22.39,
      "datatype": "float",
      "quality": "StatusCode(value=0)"
    }
  ]
}
```

### Node Metadata: nodesfile.json

Defines node properties:
- Node IDs
- Display names
- Data types
- Descriptions

### OPC-UA Definitions: BoilerModel2.NodeSet2.xml

Standard OPC-UA node definitions in XML format.

## Architecture

```
INPUT FILES (JSON, XML)
    ↓
DATA NORMALIZER
    ↓
NODE RESOLVER
    ↓
MACHINE STATE ENGINE ─┐
ALARM ENGINE         ├─→ CONTEXT BUILDER
TREND ENGINE         │
ANOMALY ENGINE       │
HEALTH ENGINE        ┘
    ↓
LLM-READY CONTEXT
    ↓
┌─────────────┬──────────────┬─────────────┐
│  Dashboard  │   REST API   │   Reports   │
└─────────────┴──────────────┴─────────────┘
```

## Dashboard Tabs

### 1. Real-Time Graphs
- All machine variables plotted over time
- Min/Max/Average values displayed
- Color-coded by variable
- Interactive matplotlib figures

### 2. Current Readings
- Latest value for each sensor
- Units and trends
- Communication quality
- Data quality status

### 3. Alarm Timeline
- Complete chronological alarm history
- Timestamp for each alarm
- Value that triggered alarm
- Threshold information
- Color-coded by severity

### 4. Health Status
- Overall health score (0-100)
- Machine state (RUNNING, IDLE, WARNING, CRITICAL)
- Health factors with explanations
- Active alarm count
- Anomaly count

## Alarm Detection

Alarms trigger when sensor values cross configured thresholds:

```
[19:13:37] Pressure : 0.783bar
[!] WARNING GENERATED
Reason: Pressure fallen below threshold (0.8 bar)
```

All thresholds are configurable in `config.yaml`:

```yaml
engines:
  alarm:
    thresholds:
      Temperature:
        high: 25.0      # High alarm
        low: 15.0       # Low alarm
```

## Output Files

When using `generate_report.py`:

- `machine_context_report.txt` - Professional formatted report
- `context.json` - Structured machine context (JSON)
- `summary.txt` - Text summary of findings

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/engine/status` | GET | Engine status |
| `/context` | GET | Complete machine context |
| `/context/llm` | GET | LLM-ready context string |
| `/machine/state` | GET | Current machine state |
| `/machine/health` | GET | Health status |
| `/alarms` | GET | Active alarms |
| `/events` | GET | Recent events |
| `/anomalies` | GET | Detected anomalies |
| `/nodes` | GET | Registered nodes |
| `/readings` | GET | Current readings |
| `/trends` | GET | Current trends |
| `/process` | POST | Process new data file |

## Python Integration

```python
from app.main import MachineContextEngine

# Initialize
engine = MachineContextEngine(
    config_file="config.yaml",
    node_metadata_json="nodesfile.json",
    node_metadata_xml="BoilerModel2.NodeSet2 (1).xml"
)

# Process data
context = engine.process("machine_data_5min.json")

# Access results
print(f"Machine state: {context.machine_state}")
print(f"Health score: {context.health_score}")
print(f"Active alarms: {len(context.active_alarms)}")
print(f"Anomalies: {len(context.anomalies)}")

# Get LLM context
llm_context = engine.get_llm_context()
print(llm_context)
```

## Graph Visualization

The dashboard includes:

- **Temperature Graph** - Temperature over 5 minutes with trend line
- **Pressure Graph** - Pressure readings and statistics
- **Motor Speed Graph** - RPM trend with min/max/avg
- **Motor Current Graph** - Current consumption pattern
- **Vibration Graph** - Vibration levels with anomaly highlights
- **Machine Status Graph** - State changes over time

Each graph shows:
- Min/Max/Average values
- Trend direction (↗ up, ↘ down, → stable)
- Grid for easy reading
- Color-coded lines for quick identification

## Performance

- Processes 1,800 readings (5 min @ 1 sec sampling) in < 1 second
- Dashboard loads in < 2 seconds
- Report generation in < 1 second
- Lightweight dependencies (no heavy frameworks)

## Troubleshooting

**UI won't load:**
```bash
# Verify dependencies
python test_ui.py

# Install missing packages
pip install -r requirements.txt --upgrade
```

**Alarms not detecting:**
- Check `config.yaml` thresholds
- Verify data range in graphs
- Adjust thresholds to match your data range

**Graphs not showing data:**
- Ensure `machine_data_5min.json` is in the working directory
- Check that data format matches expected schema
- Verify node IDs match in metadata files

## License

MIT License

## Support

For issues or questions, check the generated report or dashboard for detailed diagnostics.
