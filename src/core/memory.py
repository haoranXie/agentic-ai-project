import time
import random
from typing import Dict, List, Optional

class Memory:
    def __init__(self):
        self.past_interactions = []
        self.emotional_states = {}
        self.agent_responses = []
        self.biometric_data = []
        self.coherence_events = []
        
        # Biometric simulation parameters
        self.hrv_baseline = 50
        self.current_hrv = self.hrv_baseline
        self.stress_level = 0.0

    def store_interaction(self, interaction: str, emotional_analysis: Dict = None, turn_number: int = 0):
        """Store user interaction with enhanced metadata"""
        entry = {
            "interaction": interaction,
            "timestamp": time.time(),
            "turn_number": turn_number,
            "emotional_analysis": emotional_analysis,
            "biometric_snapshot": self.get_current_biometrics()
        }
        self.past_interactions.append(entry)
        
        # Update stress level based on emotional state
        if emotional_analysis:
            self._update_stress_level(emotional_analysis)

    def store_agent_response(self, agent_name: str, response: str, response_type: str = "normal"):
        """Store agent response with metadata"""
        entry = {
            "agent_name": agent_name,
            "response": response,
            "response_type": response_type,
            "timestamp": time.time(),
            "turn_number": len(self.past_interactions)
        }
        self.agent_responses.append(entry)

    def store_coherence_event(self, event_type: str, details: Dict):
        """Store coherence-related events (drift, recursion, etc.)"""
        event = {
            "event_type": event_type,
            "details": details,
            "timestamp": time.time(),
            "turn_number": len(self.past_interactions)
        }
        self.coherence_events.append(event)

    def update_emotional_state(self, agent_name: str, emotional_state: str):
        """Update emotional state for an agent"""
        self.emotional_states[agent_name] = {
            "state": emotional_state,
            "timestamp": time.time(),
            "turn_number": len(self.past_interactions)
        }

    def simulate_biometric_response(self, emotional_intensity: float, stress_factor: float = 0.0):
        """Simulate biometric response to emotional state"""
        # Simulate HRV changes based on emotional state
        hrv_change = random.uniform(-10, 5) - (emotional_intensity * 15) - (stress_factor * 10)
        self.current_hrv = max(20, min(80, self.current_hrv + hrv_change))
        
        # Generate simulated biometric data
        biometric_entry = {
            "hrv": round(self.current_hrv, 1),
            "heart_rate": random.randint(60, 100) + int(stress_factor * 20),
            "gsr": random.uniform(0.1, 1.0) + stress_factor,
            "timestamp": time.time(),
            "stress_level": self.stress_level,
            "emotional_intensity": emotional_intensity
        }
        
        self.biometric_data.append(biometric_entry)
        return biometric_entry

    def get_current_biometrics(self) -> Dict:
        """Get current biometric readings"""
        if self.biometric_data:
            return self.biometric_data[-1]
        else:
            # Return baseline values
            return {
                "hrv": self.hrv_baseline,
                "heart_rate": 70,
                "gsr": 0.3,
                "stress_level": 0.0,
                "timestamp": time.time()
            }

    def _update_stress_level(self, emotional_analysis: Dict):
        """Update stress level based on emotional analysis"""
        stress_factors = {
            "angry": 0.8,
            "anxious": 0.9,
            "sad": 0.6,
            "confused": 0.5,
            "happy": -0.2,
            "neutral": -0.1
        }
        
        emotional_state = emotional_analysis.get("emotional_state", "neutral")
        base_stress = stress_factors.get(emotional_state, 0.0)
        
        # Additional stress from coherence issues
        if emotional_analysis.get("coherence_status") == "coherence_lost":
            base_stress += 0.3
        if emotional_analysis.get("recursion_detected"):
            base_stress += 0.2
        if emotional_analysis.get("drift_detected"):
            base_stress += 0.2
            
        # Gradually adjust stress level
        self.stress_level = max(0.0, min(1.0, self.stress_level * 0.8 + base_stress * 0.2))

    def get_past_interactions(self, limit: int = None) -> List[Dict]:
        """Get past interactions with optional limit"""
        if limit:
            return self.past_interactions[-limit:]
        return self.past_interactions

    def get_emotional_state(self, agent_name: str) -> Optional[Dict]:
        """Get current emotional state for an agent"""
        return self.emotional_states.get(agent_name, None)

    def get_conversation_context(self, turns: int = 3) -> Dict:
        """Get recent conversation context for agents"""
        recent_interactions = self.get_past_interactions(turns)
        recent_responses = self.agent_responses[-turns:] if len(self.agent_responses) >= turns else self.agent_responses
        recent_events = self.coherence_events[-turns:] if len(self.coherence_events) >= turns else self.coherence_events
        
        return {
            "recent_interactions": recent_interactions,
            "recent_responses": recent_responses,
            "recent_events": recent_events,
            "current_biometrics": self.get_current_biometrics(),
            "stress_level": self.stress_level
        }

    def get_emotional_trend(self, turns: int = 5) -> List[str]:
        """Get emotional trend over recent turns"""
        recent = self.get_past_interactions(turns)
        return [
            interaction.get("emotional_analysis", {}).get("emotional_state", "unknown")
            for interaction in recent
            if interaction.get("emotional_analysis")
        ]

    def is_biometric_alert(self) -> bool:
        """Check if biometric data indicates stress"""
        current = self.get_current_biometrics()
        return (
            current["hrv"] < 35 or 
            current["heart_rate"] > 90 or 
            self.stress_level > 0.7
        )

    def get_memory_summary(self) -> Dict:
        """Get summary of all stored memory"""
        return {
            "total_interactions": len(self.past_interactions),
            "total_responses": len(self.agent_responses),
            "coherence_events": len(self.coherence_events),
            "current_stress_level": round(self.stress_level, 2),
            "current_hrv": self.get_current_biometrics()["hrv"],
            "emotional_trend": self.get_emotional_trend(),
            "biometric_alert": self.is_biometric_alert()
        }