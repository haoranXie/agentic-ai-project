from flask import Flask, request, jsonify, render_template_string
import sys
import os
import time
from typing import Dict, List

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from agents.specialized_agents import AgentA, AgentB
from core.memory import Memory
from core.reasoning import Reasoning
from utils.config import load_config

app = Flask(__name__)

# Initialize the AI system
config = load_config()
memory = Memory()
reasoning = Reasoning()

# Initialize agents
agent_a_config = config['agent_parameters']['agent_a']
agent_b_config = config['agent_parameters']['agent_b']

agent_a = AgentA(name=agent_a_config['name'], tone=agent_a_config['tone'])
agent_b = AgentB(name=agent_b_config['name'], tone=agent_b_config['tone'])

# Global turn counter for the API
turn_counter = 0

@app.route('/', methods=['GET'])
def dashboard():
    """Simple web dashboard for the agentic AI system"""
    dashboard_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Coherence Protocol - Agentic AI Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; }
            .header { text-align: center; color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            .chat-container { display: flex; gap: 20px; margin: 20px 0; }
            .chat-box { flex: 1; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
            .input-section { margin: 20px 0; }
            .input-section input { width: 70%; padding: 10px; font-size: 16px; }
            .input-section button { padding: 10px 20px; font-size: 16px; background: #3498db; color: white; border: none; cursor: pointer; }
            .status-panel { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 10px 0; }
            .alert { padding: 10px; margin: 5px 0; border-radius: 5px; }
            .alert-warning { background: #f39c12; color: white; }
            .alert-danger { background: #e74c3c; color: white; }
            .alert-info { background: #3498db; color: white; }
            .response { margin: 10px 0; padding: 10px; border-left: 4px solid #3498db; background: #f8f9fa; }
            .intervention { border-left-color: #f39c12; background: #fff3cd; }
            .hidden { display: none; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Coherence Protocol - Agentic AI System</h1>
                <p>Emotion-Recursive Agent Loop with Drift Detection</p>
            </div>
            
            <div class="input-section">
                <input type="text" id="userInput" placeholder="Type your message here..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
                <button onclick="getStatus()">System Status</button>
                <button onclick="runDemo()">Run Demo</button>
            </div>
            
            <div class="status-panel" id="statusPanel">
                <h3>System Status</h3>
                <div id="systemStatus">Ready to begin conversation...</div>
            </div>
            
            <div class="chat-container">
                <div class="chat-box">
                    <h3>Conversation</h3>
                    <div id="conversationHistory"></div>
                </div>
                
                <div class="chat-box">
                    <h3>Monitoring</h3>
                    <div id="monitoringAlerts"></div>
                </div>
            </div>
        </div>
        
        <script>
            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
            
            async function sendMessage() {
                const input = document.getElementById('userInput');
                const message = input.value.trim();
                if (!message) return;
                
                input.value = '';
                addToConversation('You: ' + message, 'user');
                
                try {
                    const response = await fetch('/api/send_input', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ input: message })
                    });
                    
                    const data = await response.json();
                    
                    // Display agent responses
                    if (data.agent_a_response) {
                        addToConversation('Agent A: ' + data.agent_a_response, 'agent');
                    }
                    
                    if (data.agent_b_response) {
                        addToConversation('Agent B (Monitor): ' + data.agent_b_response, 'intervention');
                    }
                    
                    // Display alerts
                    if (data.alerts && data.alerts.length > 0) {
                        showAlerts(data.alerts);
                    }
                    
                    // Update status
                    updateStatus(data.status);
                    
                } catch (error) {
                    console.error('Error:', error);
                    addToConversation('System Error: Could not process message', 'error');
                }
            }
            
            async function getStatus() {
                try {
                    const response = await fetch('/api/system_status');
                    const data = await response.json();
                    updateStatus(data);
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            async function runDemo() {
                try {
                    const response = await fetch('/api/run_demo', { method: 'POST' });
                    const data = await response.json();
                    
                    if (data.demo_results) {
                        data.demo_results.forEach(result => {
                            addToConversation('Demo: ' + result.input, 'user');
                            if (result.agent_a_response) {
                                addToConversation('Agent A: ' + result.agent_a_response, 'agent');
                            }
                            if (result.agent_b_response) {
                                addToConversation('Agent B: ' + result.agent_b_response, 'intervention');
                            }
                            if (result.alerts && result.alerts.length > 0) {
                                showAlerts(result.alerts);
                            }
                        });
                    }
                    
                } catch (error) {
                    console.error('Error:', error);
                }
            }
            
            function addToConversation(message, type) {
                const history = document.getElementById('conversationHistory');
                const div = document.createElement('div');
                div.className = 'response ' + (type === 'intervention' ? 'intervention' : '');
                div.textContent = message;
                history.appendChild(div);
                history.scrollTop = history.scrollHeight;
            }
            
            function showAlerts(alerts) {
                const alertDiv = document.getElementById('monitoringAlerts');
                alerts.forEach(alert => {
                    const div = document.createElement('div');
                    div.className = 'alert alert-warning';
                    div.textContent = alert;
                    alertDiv.appendChild(div);
                });
            }
            
            function updateStatus(status) {
                const statusDiv = document.getElementById('systemStatus');
                statusDiv.innerHTML = `
                    <p><strong>Total Interactions:</strong> ${status.total_interactions || 0}</p>
                    <p><strong>Coherence Events:</strong> ${status.coherence_events || 0}</p>
                    <p><strong>Current Stress Level:</strong> ${status.stress_level || 0}</p>
                    <p><strong>OpenAI Available:</strong> ${status.llm_available ? 'Yes' : 'No'}</p>
                    <p><strong>Emotional Progression:</strong> ${(status.emotional_progression || []).join(' → ')}</p>
                `;
            }
        </script>
    </body>
    </html>
    """
    return dashboard_html

@app.route('/api/send_input', methods=['POST'])
def send_input():
    """Process user input through the agentic AI system"""
    global turn_counter
    
    try:
        user_input = request.json.get('input', '')
        if not user_input:
            return jsonify({'error': 'No input provided'}), 400
        
        turn_counter += 1
        
        # Process through reasoning system
        emotional_analysis = reasoning.analyze_input(user_input, turn_counter)
        
        # Calculate emotional intensity and simulate biometrics
        emotional_intensity = calculate_emotional_intensity(emotional_analysis)
        stress_factor = emotional_analysis.get("coherence_status") != "stable"
        biometric_data = memory.simulate_biometric_response(emotional_intensity, stress_factor * 0.5)
        
        # Store interaction
        memory.store_interaction(user_input, emotional_analysis, turn_counter)
        
        # Get memory context
        memory_context = memory.get_conversation_context()
        
        # Agent A responds
        agent_a_response = agent_a.respond(user_input, emotional_analysis, memory_context)
        memory.store_agent_response(agent_a.name, agent_a_response, "supportive")
        
        # Agent B monitors and potentially intervenes
        monitoring_result = agent_b.monitor_emotional_drift(
            memory.get_past_interactions(), 
            emotional_analysis
        )
        
        agent_b_response = None
        if monitoring_result.get("intervention_needed"):
            agent_b_response = agent_b.recursive_response(
                user_input, emotional_analysis, monitoring_result
            )
            if agent_b_response:
                memory.store_agent_response(agent_b.name, agent_b_response, "intervention")
        
        # Prepare response
        response_data = {
            'agent_a_response': agent_a_response,
            'agent_b_response': agent_b_response,
            'emotional_analysis': emotional_analysis,
            'alerts': emotional_analysis.get('alerts', []),
            'biometric_data': biometric_data,
            'monitoring_result': monitoring_result,
            'status': get_system_status_data()
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': f'Processing error: {str(e)}'}), 500

@app.route('/api/system_status', methods=['GET'])
def get_system_status():
    """Get comprehensive system status"""
    return jsonify(get_system_status_data())

@app.route('/api/run_demo', methods=['POST'])
def run_demo():
    """Run automated demo scenarios"""
    global turn_counter
    
    demo_scenarios = [
        "I'm feeling great today, everything is going well!",
        "Actually, I'm not sure... maybe I'm not feeling that great",
        "I keep thinking about this over and over, I can't stop worrying about it",
        "I love my job but I also hate it, I don't know what to think",
        "I'm fine, everything is fine, but nothing feels right"
    ]
    
    demo_results = []
    
    try:
        for scenario in demo_scenarios:
            turn_counter += 1
            
            # Process scenario
            emotional_analysis = reasoning.analyze_input(scenario, turn_counter)
            emotional_intensity = calculate_emotional_intensity(emotional_analysis)
            stress_factor = emotional_analysis.get("coherence_status") != "stable"
            
            memory.simulate_biometric_response(emotional_intensity, stress_factor * 0.5)
            memory.store_interaction(scenario, emotional_analysis, turn_counter)
            
            memory_context = memory.get_conversation_context()
            
            # Get agent responses
            agent_a_response = agent_a.respond(scenario, emotional_analysis, memory_context)
            memory.store_agent_response(agent_a.name, agent_a_response, "supportive")
            
            monitoring_result = agent_b.monitor_emotional_drift(
                memory.get_past_interactions(), 
                emotional_analysis
            )
            
            agent_b_response = None
            if monitoring_result.get("intervention_needed"):
                agent_b_response = agent_b.recursive_response(
                    scenario, emotional_analysis, monitoring_result
                )
                if agent_b_response:
                    memory.store_agent_response(agent_b.name, agent_b_response, "intervention")
            
            demo_results.append({
                'input': scenario,
                'agent_a_response': agent_a_response,
                'agent_b_response': agent_b_response,
                'alerts': emotional_analysis.get('alerts', []),
                'emotional_state': emotional_analysis.get('emotional_state', 'neutral')
            })
        
        return jsonify({
            'demo_results': demo_results,
            'final_status': get_system_status_data()
        })
        
    except Exception as e:
        return jsonify({'error': f'Demo error: {str(e)}'}), 500

@app.route('/api/reset_system', methods=['POST'])
def reset_system():
    """Reset the system state"""
    global turn_counter
    
    try:
        # Reset components
        global memory, reasoning
        memory = Memory()
        reasoning = Reasoning()
        turn_counter = 0
        
        return jsonify({'message': 'System reset successfully'})
        
    except Exception as e:
        return jsonify({'error': f'Reset error: {str(e)}'}), 500

def calculate_emotional_intensity(emotional_analysis: Dict) -> float:
    """Calculate emotional intensity from analysis"""
    base_intensity = {
        "happy": 0.3,
        "sad": 0.7,
        "angry": 0.8,
        "anxious": 0.9,
        "confused": 0.6,
        "neutral": 0.1
    }
    
    intensity = base_intensity.get(emotional_analysis.get("emotional_state", "neutral"), 0.5)
    
    # Increase intensity based on coherence issues
    if emotional_analysis.get("coherence_status") == "coherence_lost":
        intensity += 0.3
    if emotional_analysis.get("recursion_detected"):
        intensity += 0.2
    if emotional_analysis.get("drift_detected"):
        intensity += 0.2
        
    return min(1.0, intensity)

def get_system_status_data() -> Dict:
    """Get system status data"""
    memory_summary = memory.get_memory_summary()
    conv_summary = reasoning.get_conversation_summary()
    agent_a_status = agent_a.get_agent_status()
    agent_b_status = agent_b.get_monitoring_summary()
    
    return {
        'total_interactions': memory_summary['total_interactions'],
        'coherence_events': memory_summary['coherence_events'],
        'stress_level': memory_summary['current_stress_level'],
        'biometric_alert': memory_summary['biometric_alert'],
        'emotional_progression': memory_summary['emotional_trend'],
        'llm_available': agent_a_status.get('llm_available', False),
        'agent_a_responses': agent_a_status['response_count'],
        'agent_b_alerts': agent_b_status['total_alerts'],
        'recursion_count': conv_summary['recursion_count'],
        'last_emotional_state': conv_summary['last_emotional_state'],
        'turn_count': turn_counter
    }

if __name__ == '__main__':
    print("Starting Coherence Protocol Agentic AI API...")
    print("Web Dashboard: http://localhost:5000")
    print("API Endpoint: http://localhost:5000/api/send_input")
    print("System Status: http://localhost:5000/api/system_status")
    
    app.run(debug=True, host='0.0.0.0', port=5000)