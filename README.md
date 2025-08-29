# 📞 Interactive Call Analysis Dashboard

An interactive visualization tool for analyzing overtalk and silence metrics in call logs. This system provides comprehensive analysis of conversation dynamics with visual timelines and detailed metrics.

## ✨ Features

- **📊 Interactive Timeline Visualization**: Visual representation of call conversations with color-coded speakers
- **🟠 Overtalk Detection**: Identifies and visualizes when speakers talk simultaneously
- **⚫ Silence Analysis**: Detects and measures silence gaps in conversations
- **📈 Comprehensive Metrics**: Calculate percentage distributions of talk time, overlaps, and silences
- **🎛️ Interactive Controls**: Adjustable silence threshold and conversation selection
- **📝 Detailed Analysis**: Tabular breakdown of all detected incidents
- **🌐 Streamlit Integration**: Web-based dashboard for easy interaction

## 🚀 Quick Start

### Prerequisites

- Python 3.12 or higher
- Required packages (automatically installed):
  - `streamlit>=1.28.0`
  - `plotly>=5.17.0`
  - `pandas>=2.1.0`

### Installation

1. **Clone or navigate to the project directory**
```bash
cd /workspace/prodigal
```

2. **Install dependencies**
```bash
pip install -e .
# OR using uv
uv pip install -e .
```

3. **Run the application**
```bash
# Option 1: Interactive launcher
python main.py

# Option 2: Direct Streamlit launch
streamlit run call_analysis_viz.py

# Option 3: Test with demo data
python demo_analyzer.py
```

## 📊 Visualization Features

### Timeline Visualization
- **🔴 Red bars**: Agent speaking segments
- **🟢 Green bars**: Customer speaking segments
- **🟠 Orange indicators**: Overlap periods (overtalk)
- **⚫ Gray indicators**: Silence periods

### Interactive Controls
- **Call Selection**: Choose from available conversation files
- **Silence Threshold**: Adjust minimum duration (0.1-5.0 seconds) to be considered silence
- **Hover Details**: Interactive tooltips showing segment details

### Metrics Dashboard
- **Talk Time Distribution**: Pie chart showing time allocation
- **Percentage Breakdown**: Bar chart of key metrics
- **Detailed Tables**: Comprehensive breakdown of overlaps and silences

## 📈 Key Metrics Calculated

1. **Total Call Duration**: Complete conversation length
2. **Overlap Percentage**: Time when both speakers talk simultaneously
3. **Silence Percentage**: Time with no active speech
4. **Agent/Customer Talk Ratio**: Speaking time distribution
5. **Incident Counts**: Number of overlaps and silence periods

## 📁 Data Format

The system expects JSON files with the following structure:

```json
[
    {
        "speaker": "Agent",
        "text": "Hello, this is Mark from XYZ Collections...",
        "stime": 0,
        "etime": 7
    },
    {
        "speaker": "Customer", 
        "text": "Yes, this is Jessica. What is this about?",
        "stime": 8,
        "etime": 13
    }
]
```

**Fields:**
- `speaker`: "Agent" or "Customer"
- `text`: Transcript of the speech segment
- `stime`: Start time in seconds
- `etime`: End time in seconds

## 🎯 Use Cases

### Quality Assurance
- **Overtalk Analysis**: Identify when agents interrupt customers
- **Silence Detection**: Find awkward pauses or technical issues
- **Talk Time Balance**: Ensure appropriate conversation flow

### Training & Coaching
- **Communication Skills**: Analyze listening vs talking patterns
- **Professional Behavior**: Identify areas for improvement
- **Best Practices**: Compare successful vs challenging calls

### Performance Metrics
- **Agent Evaluation**: Measure professional communication habits
- **Call Quality**: Assess overall conversation dynamics
- **Benchmarking**: Compare against standards or peer performance

## 🔧 Advanced Usage

### Custom Silence Thresholds
Adjust the silence detection sensitivity:
- **0.1-0.5s**: Detect brief pauses (natural speech gaps)
- **0.5-1.0s**: Standard silence detection
- **1.0s+**: Only significant pauses

### Batch Analysis
Process multiple conversations:
```python
from call_analysis_viz import CallAnalyzer
import json

# Analyze multiple files
results = {}
for file_path in conversation_files:
    with open(file_path) as f:
        data = json.load(f)
    analyzer = CallAnalyzer(data)
    results[file_path] = analyzer.calculate_metrics()
```

## 📊 Example Analysis

Using the provided sample conversation:

```
🎯 CALL METRICS SUMMARY:
────────────────────────────────────────
📊 Total Call Duration: 72.0 seconds
🔴 Agent Speaking Time: 36.0s (50.0%)
🟢 Customer Speaking Time: 21.0s (29.2%)
🟠 Total Overlap Time: 3.0s (4.2%)
⚫ Total Silence Time: 12.0s (16.7%)
```

## 🛠️ Technical Architecture

### Core Components

1. **CallAnalyzer**: Main analysis engine
   - Timeline processing
   - Overlap detection algorithm
   - Silence gap calculation
   - Metrics computation

2. **Visualization Engine**: Plotly-based charts
   - Interactive timeline plots
   - Multi-subplot layouts
   - Hover interactions
   - Color-coded segments

3. **Streamlit Interface**: Web dashboard
   - File selection
   - Parameter controls
   - Real-time updates
   - Export capabilities

### Algorithms

**Overlap Detection**: Compares segment end times with subsequent start times
**Silence Detection**: Identifies gaps between consecutive segments above threshold
**Metrics Calculation**: Percentage-based analysis of time allocations

## 🤝 Contributing

To extend the functionality:

1. **Add New Metrics**: Extend the `calculate_metrics()` method
2. **Custom Visualizations**: Create new Plotly chart functions
3. **Export Features**: Add data export capabilities
4. **Advanced Analytics**: Implement pattern recognition algorithms

## 📞 Support

For issues or questions:
- Check conversation file format compliance
- Verify all required dependencies are installed
- Ensure Python 3.12+ compatibility
- Review Streamlit configuration

## 📄 License

This project is designed for call center quality analysis and training purposes.
