## Overview
An agent system that detects emotional drift, recursion patterns, and coherence loss in real-time conversations with biometric simulation and intervention protocols.

### Two-Agent System
- **Agent A (Axis)** - Agent AI-powered responses based off several factors
- **Agent B (M)** - Agents monitors for drift, recursion, and interventions

### Key Capabilities
- **Emotional Drift Detection**: Tracks rapid emotional state changes
- **Recursion Detection**: Identifies repetitive thought patterns
- **Contradiction Analysis**: Spots conflicting emotional statements
- **Biometric Simulation**: HRV and stress level tracking
- **Intervention Protocols**: Automated grounding suggestions

## Features
- OpenAI LLM integration with fallback to rule-based responses
- Real-time emotional monitoring and biometric simulation
- Color-coded terminal interface with web dashboard
- Automated demo scenarios for testing drift detection

## Project Structure
```
src/
├── agents/           # AgentA (Axis) & AgentB (M) implementations
├── core/             # LLM service, memory, reasoning
├── interfaces/       # Web API and dashboard
├── utils/            # Configuration management
└── main.py          # System orchestrator
```

## Installation & Usage

1. **Setup Environment:**
   ```bash
   python -m venv env_agentic_ai
   env_agentic_ai\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

2. **Configure (Optional):**
   - Add OpenAI API key to `config/settings.yaml`

3. **Run System:**
   ```bash
   python src/main.py
   ```

### Commands
- `demo` - Run automated drift detection scenarios
- `api` - Start web interface at http://localhost:5000
- `status` - Show system status
- `quit` - Exit

## Technical Implementation

### Core Algorithms
1. **Emotional State Analysis** - Multi-dimensional emotion mapping with context awareness
2. **Drift Detection** - Sliding window analysis for contradictions and recursion patterns
3. **Intervention Protocols** - Graduated response system with biometric triggers

### Example Outputs
```
Agent A: "I notice you might be caught in a thought loop. 
         Would it help to pause and take a few deep breaths?"

Agent B: "Recursion Detected at Turn 3"
         "Coherence Lost – Recommend Pause"
```

### Demo Scenarios (3 Turns)
1. Positive → Uncertain Drift
2. Recursive thought loops
3. Coherence loss detection

## Configuration

Key parameters in `config/settings.yaml`:
```yaml
emotional_drift:
  recursion_threshold: 2      # Turns before recursion alert
  
biometric_simulation:
  hrv_baseline: 50           # Normal HRV range
  stress_threshold: 35       # Alert threshold
  
openai:
  api_key: "your-key-here"   # Optional LLM integration
```

