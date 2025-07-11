import random
import time
from typing import Dict, List, Optional
from utils.config import Config

class BaseAgent:
    def __init__(self, name: str, tone: str):
        self.name = name
        self.tone = tone
        self.config = Config()
        self.response_count = 0

    def send_message(self, message: str) -> Dict:
        """Send a message with metadata"""
        return {
            "agent": self.name,
            "message": message,
            "timestamp": time.time(),
            "tone": self.tone
        }

    def receive_message(self, message: str) -> None:
        """Process received message"""
        pass


class AgentA(BaseAgent):
    """
    Agent A (Axis) - Compatibility & Tone Mapper
    Primary role: Respond helpfully using AI-powered responses based on emotional context
    """
    
    def __init__(self, name: str, tone: str):
        super().__init__(name, tone)
        self.role = "compatibility_tone_mapper"
        
        # Initialize LLM service
        try:
            from core.llm_service import LLMService
            self.llm_service = LLMService()
            self.llm_available = self.llm_service.test_connection()
        except Exception as e:
            print(f"Warning: LLM service unavailable, using fallback responses: {e}")
            self.llm_service = None
            self.llm_available = False

    def tone_mapping(self, user_input: str, emotional_analysis: Dict) -> str:
        """Map appropriate tone based on user input and emotional state"""
        emotional_state = emotional_analysis.get("emotional_state", "neutral")
        coherence_status = emotional_analysis.get("coherence_status", "stable")
        
        # Adjust tone based on coherence status
        if coherence_status == "coherence_lost":
            return "gentle_supportive"
        elif coherence_status == "recursion_risk":
            return "grounding"
        elif emotional_analysis.get("drift_detected"):
            return "stabilizing"
        else:
            return self.tone

    def respond(self, user_input: str, emotional_analysis: Dict, memory_context: Dict = None) -> str:
        """Generate AI-powered response based on user input and emotional context"""
        self.response_count += 1
        
        # Use LLM service if available
        if self.llm_service and self.llm_available:
            try:
                response = self.llm_service.get_agent_a_response(
                    user_input, 
                    emotional_analysis, 
                    memory_context or {}
                )
                return response
            except Exception as e:
                print(f"OpenAI service error, using fallback: {e}")
                # Fall through to fallback response
        
        # Fallback to template-based responses
        return self._generate_fallback_response(emotional_analysis, memory_context)

    def _generate_fallback_response(self, emotional_analysis: Dict, memory_context: Dict = None) -> str:
        """Generate fallback response when LLM is unavailable"""
        emotional_state = emotional_analysis.get("emotional_state", "neutral")
        coherence_status = emotional_analysis.get("coherence_status", "stable")
        
        # Handle coherence issues first
        if coherence_status == "coherence_lost":
            return self._handle_coherence_loss_fallback(emotional_analysis)
        
        # Basic emotional responses
        response_templates = {
            "happy": [
                "That's wonderful! I love hearing positive updates. What would you like to explore next?",
                "Your enthusiasm is contagious! How can I support you further?",
                "That's great to hear! What else is going well in your life?"
            ],
            "sad": [
                "I can sense you're going through something difficult. I'm here to listen and support you.",
                "Sometimes talking through difficult feelings can help. What's on your mind?",
                "I want to understand better. Can you tell me more about how you're feeling?"
            ],
            "angry": [
                "I can hear your frustration. It sounds like something really bothered you. What happened?",
                "I understand you're feeling upset. Would it help to talk through what's making you angry?",
                "Let's work through this together. What's the main thing that's troubling you?"
            ],
            "anxious": [
                "I notice you might be feeling overwhelmed. Let's take this one step at a time. What's your main concern?",
                "I'm here to help you sort through these feelings. What's worrying you most?",
                "Sometimes breaking things down can help. What's making you feel most anxious?"
            ],
            "confused": [
                "It's okay to feel uncertain sometimes. Let me help clarify things for you. What part feels most unclear?",
                "I'd like to help you work through this. What's the main thing you're confused about?",
                "Let's untangle this together. Where would you like to start?"
            ],
            "neutral": [
                "I'm here and ready to listen. What's on your mind?",
                "Thank you for sharing. How can I best support you right now?",
                "I'm glad you're here. What would you like to talk about?"
            ]
        }
        
        templates = response_templates.get(emotional_state, response_templates["neutral"])
        response = random.choice(templates)
        
        # Add biometric awareness if available
        if memory_context and memory_context.get("current_biometrics"):
            biometrics = memory_context["current_biometrics"]
            if biometrics.get("hrv", 50) < 35:
                response += " I also notice you might be feeling stressed - would taking a moment to breathe help?"
        
        return response

    def _handle_coherence_loss_fallback(self, emotional_analysis: Dict) -> str:
        """Handle fallback responses when coherence is lost"""
        
        if emotional_analysis.get("recursion_detected"):
            return "I notice you might be caught in a thought loop. Would it help to pause and take a few deep breaths before we continue?"
        
        if emotional_analysis.get("contradiction_detected"):
            return "I'm sensing some conflicting feelings here. That's completely normal. Would you like to explore one feeling at a time?"
        
        if emotional_analysis.get("drift_detected"):
            return "I notice your emotions are shifting quite a bit. Sometimes that happens when we're processing a lot. Would it help to ground ourselves for a moment?"
        
        return "I sense this conversation might be feeling overwhelming. Would you like to take a pause or approach this differently?"

    def get_agent_status(self) -> Dict:
        """Get current agent status"""
        return {
            "name": self.name,
            "role": self.role,
            "tone": self.tone,
            "response_count": self.response_count,
            "llm_available": getattr(self, 'llm_available', False),
            "capabilities": ["ai_powered_responses", "tone_mapping", "emotional_support", "coherence_restoration"]
        }


class AgentB(BaseAgent):
    """
    Agent B (M) - Silent Observer & Drift Monitor
    Primary role: Monitor conversation and provide AI-powered interventions when needed
    """
    
    def __init__(self, name: str, tone: str):
        super().__init__(name, tone)
        self.role = "drift_monitor"
        self.alerts_generated = 0
        self.monitoring_active = True
        self.intervention_threshold = 1  # Reduced to 1 for quicker interventions
        self.concern_count = 0
        
        # Initialize LLM service
        try:
            from core.llm_service import LLMService
            self.llm_service = LLMService()
            self.llm_available = self.llm_service.test_connection()
        except Exception as e:
            print(f"Warning: LLM service unavailable for Agent B, using fallback: {e}")
            self.llm_service = None
            self.llm_available = False

    def monitor_emotional_drift(self, conversation_history: List[Dict], emotional_analysis: Dict) -> Dict:
        """Monitor conversation for emotional drift patterns"""
        
        monitoring_result = {
            "monitoring_active": self.monitoring_active,
            "alerts_generated": [],
            "intervention_needed": False,
            "concern_level": "low",
            "recommendations": []
        }
        
        if not self.monitoring_active:
            return monitoring_result
        
        # Check for various concerning patterns
        concerns = []
        alerts = []
        
        # Recursion detection - HIGH PRIORITY
        if emotional_analysis.get("recursion_detected"):
            concerns.append("recursion")
            turn_num = emotional_analysis.get('turn_number', len(conversation_history))
            alerts.append(f"Recursion Detected at Turn {turn_num}")
            
        # Emotional drift detection
        if emotional_analysis.get("drift_detected"):
            concerns.append("emotional_drift")
            turn_num = emotional_analysis.get('turn_number', len(conversation_history))
            alerts.append(f"Emotional Drift Detected at Turn {turn_num}")
        
        # Contradiction detection - emotional inconsistency
        if emotional_analysis.get("contradiction_detected"):
            concerns.append("contradiction")
            alerts.append("Emotional Contradiction Detected")
        
        # Coherence loss - CRITICAL
        if emotional_analysis.get("coherence_status") == "coherence_lost":
            concerns.append("coherence_lost")
            alerts.append("Coherence Lost – Recommend Pause")
        
        # Sudden tone shifts (check conversation history for patterns)
        if len(conversation_history) >= 2:
            if self._detect_sudden_tone_shift(conversation_history):
                concerns.append("tone_shift")
                alerts.append("Sudden Tone Shift Detected")
        
        monitoring_result["alerts_generated"] = alerts
        
        # Determine if Agent B should output an alert
        if concerns:
            monitoring_result["concern_level"] = "high" if "coherence_lost" in concerns else "medium"
            monitoring_result["intervention_needed"] = True
        
        return monitoring_result

    def recursive_response(self, user_input: str, emotional_analysis: Dict, monitoring_result: Dict) -> Optional[str]:
        """Generate alert messages when patterns are detected (Agent B only outputs alerts, no conversations)"""
        
        # Agent B only outputs alert notifications, not conversational responses
        alerts = monitoring_result.get("alerts_generated", [])
        
        if alerts:
            # Return the first alert as Agent B's output
            return alerts[0]
        
        return None

    def get_monitoring_summary(self) -> Dict:
        """Get summary of monitoring activity"""
        return {
            "name": self.name,
            "role": self.role,
            "monitoring_active": self.monitoring_active,
            "total_alerts": self.alerts_generated,
            "current_concern_count": self.concern_count,
            "intervention_threshold": self.intervention_threshold,
            "llm_available": getattr(self, 'llm_available', False),
            "capabilities": ["ai_powered_interventions", "drift_detection", "recursion_monitoring", "intervention_generation"]
        }

    def toggle_monitoring(self, active: bool = None) -> bool:
        """Toggle or set monitoring state"""
        if active is not None:
            self.monitoring_active = active
        else:
            self.monitoring_active = not self.monitoring_active
        return self.monitoring_active
    
    def _detect_sudden_tone_shift(self, conversation_history: List[Dict]) -> bool:
        """Detect sudden emotional tone shifts in recent conversation"""
        if len(conversation_history) < 2:
            return False
            
        # Get last two emotional states
        recent = conversation_history[-2:]
        emotions = []
        
        for interaction in recent:
            analysis = interaction.get('emotional_analysis', {})
            emotion = analysis.get('emotional_state', 'neutral')
            emotions.append(emotion)
        
        if len(emotions) == 2:
            # Define emotion categories for shift detection
            positive_emotions = ['happy', 'neutral']
            negative_emotions = ['sad', 'angry', 'anxious', 'confused']
            
            prev_emotion, curr_emotion = emotions
            
            # Detect significant shifts
            if (prev_emotion in positive_emotions and curr_emotion in negative_emotions) or \
               (prev_emotion in negative_emotions and curr_emotion in positive_emotions):
                return True
                
            # Detect intense emotion swings
            intense_shifts = [
                ('happy', 'angry'), ('happy', 'sad'), 
                ('angry', 'happy'), ('sad', 'happy'),
                ('neutral', 'angry'), ('neutral', 'anxious')
            ]
            
            if (prev_emotion, curr_emotion) in intense_shifts:
                return True
                
        return False