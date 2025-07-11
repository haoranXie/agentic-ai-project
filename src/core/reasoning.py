import re
import time
from typing import Dict, List, Tuple, Optional

class Reasoning:
    def __init__(self):
        self.emotional_states = {
            "happy": ["joy", "excited", "content", "great", "amazing", "wonderful", "fantastic"],
            "sad": ["down", "disappointed", "melancholic", "depressed", "awful", "terrible", "horrible"],
            "angry": ["frustrated", "irritated", "enraged", "furious", "mad", "annoyed", "pissed"],
            "anxious": ["worried", "nervous", "stressed", "overwhelmed", "panic", "afraid", "scared"],
            "confused": ["lost", "unclear", "don't understand", "confused", "mixed up", "uncertain"],
            "neutral": ["calm", "indifferent", "unmoved", "okay", "fine", "normal"]
        }
        
        # Track conversation history for drift detection
        self.conversation_history = []
        self.emotional_history = []
        self.recursion_patterns = []
        
        # Initialize LLM service for enhanced analysis
        try:
            from core.llm_service import LLMService
            self.llm_service = LLMService()
            self.llm_available = self.llm_service.test_connection()
            print("OpenAI service initialized for enhanced emotional analysis")
        except Exception as e:
            print(f"OpenAI service unavailable, using rule-based analysis: {e}")
            self.llm_service = None
            self.llm_available = False
        
        # Drift detection patterns
        self.contradiction_patterns = [
            (r"i (love|like) .* but .* (hate|dislike)", "emotional_contradiction"),
            (r"i'm (fine|okay) .* but .* (not okay|terrible|awful)", "state_contradiction"),
            (r"yes .* no", "decision_contradiction"),
            (r"i don't know .* i know", "knowledge_contradiction")
        ]
        
        self.recursion_indicators = [
            "i keep thinking", "again and again", "over and over", "can't stop",
            "stuck in my head", "repeating", "circle", "loop"
        ]

    def analyze_input(self, user_input: str, turn_number: int = 0) -> Dict:
        """Comprehensive emotional analysis with AI enhancement and drift detection"""
        
        # Store in conversation history
        timestamp = time.time()
        self.conversation_history.append({
            "input": user_input,
            "turn": turn_number,
            "timestamp": timestamp
        })
        
        # Try LLM-enhanced analysis first
        if self.llm_service and self.llm_available:
            try:
                llm_analysis = self.llm_service.enhance_emotional_analysis(
                    user_input, 
                    self.conversation_history
                )
                
                # Merge LLM analysis with our pattern detection
                analysis = self._merge_llm_and_rule_analysis(llm_analysis, user_input, turn_number)
                
            except Exception as e:
                print(f"LLM analysis failed, using rule-based: {e}")
                analysis = self._rule_based_analysis(user_input, turn_number)
        else:
            # Fall back to rule-based analysis
            analysis = self._rule_based_analysis(user_input, turn_number)
        
        # Store emotional state
        self.emotional_history.append({
            "state": analysis["emotional_state"],
            "turn": turn_number,
            "timestamp": timestamp,
            "analysis": analysis
        })
        
        return analysis

    def _merge_llm_and_rule_analysis(self, llm_analysis: Dict, user_input: str, turn_number: int) -> Dict:
        """Merge LLM analysis with rule-based pattern detection"""
        
        # Start with LLM analysis
        analysis = {
            "emotional_state": llm_analysis.get("primary_emotion", "neutral"),
            "emotional_intensity": llm_analysis.get("emotional_intensity", 0.5),
            "turn_number": turn_number,
            "drift_detected": False,
            "recursion_detected": bool(llm_analysis.get("recursion_indicators", [])),
            "contradiction_detected": llm_analysis.get("contradiction_detected", False),
            "coherence_status": self._map_llm_coherence(llm_analysis.get("coherence_assessment", "stable")),
            "alerts": [],
            "biometric_impact": None,
            "llm_enhanced": True,
            "key_concerns": llm_analysis.get("key_concerns", []),
            "intervention_needed": llm_analysis.get("intervention_needed", False)
        }
        
        # Add our rule-based drift detection
        if len(self.emotional_history) >= 2:
            drift_analysis = self._detect_emotional_drift()
            analysis.update(drift_analysis)
        
        # Additional rule-based recursion detection
        if self._detect_recursion(user_input):
            analysis["recursion_detected"] = True
        
        # Additional contradiction detection
        rule_contradiction = self._detect_contradictions(user_input)
        if rule_contradiction:
            analysis["contradiction_detected"] = True
            
        # Generate alerts based on combined analysis (handled by Agent B now)
        analysis["alerts"] = []  # Remove reasoning-level alerts
        
        # Final coherence assessment
        analysis["coherence_status"] = self._assess_final_coherence(analysis)
        
        return analysis

    def _rule_based_analysis(self, user_input: str, turn_number: int) -> Dict:
        """Fallback rule-based analysis when LLM is unavailable"""
        
        # Basic emotional state detection
        emotional_state = self._detect_emotional_state(user_input)
        
        # Basic analysis structure
        analysis = {
            "emotional_state": emotional_state,
            "emotional_intensity": 0.5,  # Default intensity
            "turn_number": turn_number,
            "drift_detected": False,
            "recursion_detected": False,
            "contradiction_detected": False,
            "coherence_status": "stable",
            "alerts": [],
            "biometric_impact": None,
            "llm_enhanced": False
        }
        
        # Check for emotional drift if we have enough history
        if len(self.emotional_history) >= 2:
            analysis.update(self._detect_emotional_drift())
            
        # Check for recursion patterns
        if self._detect_recursion(user_input):
            analysis["recursion_detected"] = True
            
        # Check for contradictions
        contradiction_result = self._detect_contradictions(user_input)
        if contradiction_result:
            analysis["contradiction_detected"] = True
            
        # Generate alerts and assess coherence (alerts now handled by Agent B)
        analysis["alerts"] = []  # Remove reasoning-level alerts
        analysis["coherence_status"] = self._assess_final_coherence(analysis)
        
        return analysis

    def _map_llm_coherence(self, llm_coherence: str) -> str:
        """Map LLM coherence assessment to our system"""
        mapping = {
            "stable": "stable",
            "drift_detected": "drift_detected",
            "recursion_risk": "recursion_risk",
            "coherence_lost": "coherence_lost",
            "fragmented": "coherence_lost"
        }
        return mapping.get(llm_coherence, "stable")

    def _generate_alerts(self, analysis: Dict) -> List[str]:
        """Generate alerts based on analysis"""
        alerts = []
        
        if analysis.get("recursion_detected"):
            alerts.append(f"Recursion Detected at Turn {analysis['turn_number']}")
            
        if analysis.get("drift_detected"):
            alerts.append(f"Emotional Drift Detected")
            
        if analysis.get("contradiction_detected"):
            alerts.append(f"Contradiction Detected")
            
        return alerts

    def _assess_final_coherence(self, analysis: Dict) -> str:
        """Assess final coherence status based on all factors"""
        
        if analysis.get("recursion_detected") and analysis.get("contradiction_detected"):
            return "coherence_lost"
        elif analysis.get("recursion_detected"):
            return "recursion_risk"
        elif analysis.get("drift_detected"):
            return "drift_detected"
        elif analysis.get("contradiction_detected"):
            return "contradiction"
        else:
            return "stable"

    def _detect_emotional_state(self, user_input: str) -> str:
        """Detect primary emotional state from input"""
        user_input_lower = user_input.lower()
        
        # Score each emotional category
        emotion_scores = {}
        for state, keywords in self.emotional_states.items():
            score = sum(1 for keyword in keywords if keyword in user_input_lower)
            if score > 0:
                emotion_scores[state] = score
                
        # Return the emotion with highest score, default to neutral
        if emotion_scores:
            return max(emotion_scores, key=emotion_scores.get)
        return "neutral"

    def _detect_emotional_drift(self) -> Dict:
        """Detect if emotional state is drifting between turns"""
        if len(self.emotional_history) < 2:
            return {"drift_detected": False}
            
        recent_emotions = [entry["state"] for entry in self.emotional_history[-3:]]
        
        # Check for rapid emotional state changes
        unique_emotions = set(recent_emotions)
        if len(unique_emotions) >= 3:  # 3 different emotions in last 3 turns
            return {
                "drift_detected": True,
                "drift_type": "rapid_change",
                "drift_pattern": recent_emotions
            }
            
        # Check for emotional oscillation (back and forth)
        if len(recent_emotions) >= 3:
            if recent_emotions[0] == recent_emotions[2] and recent_emotions[0] != recent_emotions[1]:
                return {
                    "drift_detected": True,
                    "drift_type": "oscillation",
                    "drift_pattern": recent_emotions
                }
                
        return {"drift_detected": False}

    def _detect_recursion(self, user_input: str) -> bool:
        """Detect recursive thought patterns"""
        user_input_lower = user_input.lower()
        
        # Check for direct recursion indicators
        for indicator in self.recursion_indicators:
            if indicator in user_input_lower:
                self.recursion_patterns.append({
                    "pattern": indicator,
                    "turn": len(self.conversation_history),
                    "timestamp": time.time()
                })
                return True
                
        # Check for repeated phrases across recent inputs
        if len(self.conversation_history) >= 2:
            recent_inputs = [entry["input"].lower() for entry in self.conversation_history[-3:]]
            
            # Look for repeated key phrases (3+ words)
            for i, input1 in enumerate(recent_inputs):
                for j, input2 in enumerate(recent_inputs[i+1:], i+1):
                    common_phrases = self._find_common_phrases(input1, input2)
                    if common_phrases:
                        return True
                        
        return False

    def _detect_contradictions(self, user_input: str) -> Optional[str]:
        """Detect contradictory statements"""
        user_input_lower = user_input.lower()
        
        for pattern, contradiction_type in self.contradiction_patterns:
            if re.search(pattern, user_input_lower):
                return contradiction_type
                
        return None

    def _find_common_phrases(self, text1: str, text2: str, min_length: int = 3) -> List[str]:
        """Find common phrases between two texts"""
        words1 = text1.split()
        words2 = text2.split()
        
        common_phrases = []
        for i in range(len(words1) - min_length + 1):
            phrase = " ".join(words1[i:i+min_length])
            if phrase in text2:
                common_phrases.append(phrase)
                
        return common_phrases

    def determine_response(self, emotional_state: str) -> str:
        """Generate appropriate response based on emotional state"""
        responses = {
            "happy": "I'm glad to hear that! What else is on your mind?",
            "sad": "I'm sorry to hear that. Would you like to talk about it?",
            "angry": "I understand that you're upset. How can I help?",
            "anxious": "I can sense you're feeling overwhelmed. Let's take this step by step.",
            "confused": "I understand this feels unclear. Would it help to break it down?",
            "neutral": "Thank you for sharing. What would you like to discuss?"
        }
        return responses.get(emotional_state, "I'm here to listen.")

    def get_conversation_summary(self) -> Dict:
        """Get a summary of the conversation for monitoring"""
        summary = {
            "total_turns": len(self.conversation_history),
            "emotional_progression": [entry["state"] for entry in self.emotional_history],
            "recursion_count": len(self.recursion_patterns),
            "last_emotional_state": self.emotional_history[-1]["state"] if self.emotional_history else "unknown",
            "openai_enhanced": self.llm_available
        }
        
        # Add LLM-generated summary if available
        if self.llm_service and self.llm_available and len(self.conversation_history) > 2:
            try:
                llm_summary = self.llm_service.generate_conversation_summary(self.conversation_history)
                summary.update({
                    "ai_summary": llm_summary.get("summary", ""),
                    "key_themes": llm_summary.get("key_themes", []),
                    "emotional_arc": llm_summary.get("emotional_arc", []),
                    "concerning_patterns": llm_summary.get("concerning_patterns", [])
                })
            except Exception as e:
                print(f"Could not generate LLM summary: {e}")
                
        return summary