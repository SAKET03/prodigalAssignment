# 📞 Prodigal AI Assignment - Call Analysis Suite

A comprehensive suite of tools for analyzing debt collection conversations. This project includes two main components:

1. **Debt Collection Conversation Analyzer** (Q1-2): Detects profanity and privacy compliance violations
2. **Interactive Call Analysis Dashboard** (Q3): Analyzes overtalk and silence metrics with visual timelines


```
IMPORTANT NOTE: Due to memory restriction in streamlit deploy I was not able to deploy the applications.
```

## 🚀 Quick Start

### Prerequisites

### Installation

1. **Clone repository**
```bash
git clone https://github.com/SAKET03/prodigalAssignment
cd prodigalAssignment
```

2. **Install dependencies**
```bash
apt update -y && apt upgrade -y
curl -LsSf https://astral.sh/uv/install.sh | sh
```
3. Restart Terminal

```bash
uv sync
```

4. **Set up environment variables (for LLM analysis)**
```bash
# Create .env file with your Groq API key
echo "GROQ_API_KEY=your_api_key_here" > .env
```

### Running the Applications

#### Debt Collection Analyzer (Q1-2)
```bash
uv run streamlit run Q1-2/app.py
```

#### Call Analysis Dashboard (Q3)
```bash
uv run streamlit run Q3/app.py
```


## 📈 Key Metrics Calculated

### Debt Collection Analyzer Metrics
1. **Profanity Detection**:
   - Agent profanity instances and violation rate
   - Customer profanity instances
   - Specific words/phrases identified
   - Total calls processed

2. **Privacy Compliance**:
   - Total privacy violations detected
   - Violation rate percentage
   - Compliance rate percentage
   - Sensitive information shared without verification

### Call Analysis Dashboard Metrics
1. **Total Call Duration**: Complete conversation length
2. **Overlap Percentage**: Time when both speakers talk simultaneously
3. **Silence Percentage**: Time with no active speech
4. **Agent/Customer Talk Ratio**: Speaking time distribution
5. **Incident Counts**: Number of overlaps and silence periods




