import openai
import os
import time
from typing import Dict, List, Optional
from utils.config import Config

class LLMService:
    """
    Service for interacting with OpenAI's Chat Completion API
    Handles agent responses, emotional analysis, and conversation processing
    """
    
    def __init__(self):
        self.config = Config()
        self.openai_config = self.config.get('openai', {})
        
        # Set up OpenAI client (new v1.0+ format)
        api_key = self.openai_config.get('api_key')
        
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = openai.OpenAI()  # Will use OPENAI_API_KEY env var
            
        self.model = self.openai_config.get('model', 'gpt-3.5-turbo')
        self.temperature = self.openai_config.get('temperature', 0.7)
        self.max_tokens = self.openai_config.get('max_tokens', 150)
        
        # Agent system prompts
        self.agent_a_system_prompt = """You are Agent A (Axis), a compatibility and tone mapping specialist in an agentic AI system for emotional wellness. Your role is to:

1. Respond helpfully and empathetically to user input
2. Map your tone to match the user's emotional state appropriately
3. Provide supportive, grounding responses
4. Help users process complex emotions
5. Detect when users need emotional support or intervention

Guidelines:
- Be warm, professional, and emotionally intelligent
- Adapt your communication style to the user's emotional state
- Offer practical emotional support without being clinical
- Keep responses concise but meaningful (2-3 sentences max)
- If you detect emotional distress, gently guide toward grounding techniques

Current conversation context will be provided. Respond as Agent A would."""

        self.agent_b_system_prompt = """You are Agent B (M), a silent observer and drift monitor in an agentic AI system. Your role is to:

1. Monitor conversations for emotional drift, recursion, and coherence loss
2. Only respond when intervention is necessary
3. Provide brief, grounding interventions when patterns are detected
4. Generate alerts for system monitoring

Guidelines:
- Remain mostly silent unless intervention is needed
- When you do respond, be gentle but direct
- Focus on grounding and coherence restoration
- Keep interventions brief and practical
- Your goal is to help users regain emotional stability

You will receive conversation analysis data. Only respond if intervention is warranted."""

        self.emotional_analysis_prompt = """Analyze the following user input for emotional content and patterns:

Input: "{user_input}"
Conversation history: {conversation_history}

Provide analysis in this exact JSON format:
{{
    "primary_emotion": "one of: happy, sad, angry, anxious, confused, neutral",
    "emotional_intensity": "scale 0.0-1.0",
    "contradiction_detected": "boolean",
    "recursion_indicators": "list of detected patterns",
    "coherence_assessment": "stable, drift_detected, recursion_risk, or coherence_lost",
    "key_concerns": "list of main emotional concerns",
    "intervention_needed": "boolean"
}}

Be precise and clinical in your analysis."""

    def get_agent_a_response(self, user_input: str, emotional_analysis: Dict, conversation_context: Dict) -> str:
        """Get AI-powered response from Agent A"""
        
        # Build comprehensive context for the prompt
        context_summary = self._build_context_summary(conversation_context, emotional_analysis)
        history_text = self._format_full_conversation_history(conversation_context)
        
        user_prompt = f"""
User input: "{user_input}"

Recent conversation history:
{history_text}

Emotional analysis:
- Primary emotion: {emotional_analysis.get('emotional_state', 'neutral')}
- Coherence status: {emotional_analysis.get('coherence_status', 'stable')}
- Alerts: {', '.join(emotional_analysis.get('alerts', []))}

Context: {context_summary}

As Agent A, provide a helpful, empathetic response that:
1. Acknowledges the conversation history and avoids repetition
2. Addresses the user's current emotional state
3. Provides appropriate support and engagement
4. Builds naturally on previous exchanges

Be natural, conversational, and vary your responses based on the context.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.agent_a_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Debug: Check response structure
            if not hasattr(response, 'choices'):
                raise Exception(f"OpenAI response has no choices attribute. Response type: {type(response)}")
            
            # Check if response has choices before accessing
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                raise Exception(f"OpenAI response has empty choices list. Choices length: {len(response.choices) if response.choices else 'None'}")
            
        except Exception as e:
            # Fallback to template response if OpenAI fails
            print(f"OpenAI service error, using fallback: {e}")
            return self._fallback_agent_a_response(emotional_analysis)

    def get_agent_b_intervention(self, user_input: str, emotional_analysis: Dict, monitoring_result: Dict) -> Optional[str]:
        """Get AI-powered intervention from Agent B if needed"""
        
        if not monitoring_result.get("intervention_needed", False):
            return None
            
        alerts = emotional_analysis.get('alerts', [])
        concerns = monitoring_result.get('recommendations', [])
        
        user_prompt = f"""
Analysis of concerning patterns:
- User input: "{user_input}"
- Alerts triggered: {', '.join(alerts)}
- Concern level: {monitoring_result.get('concern_level', 'low')}
- Detected issues: {', '.join(concerns)}

Emotional analysis:
- Primary emotion: {emotional_analysis.get('emotional_state', 'neutral')}
- Coherence status: {emotional_analysis.get('coherence_status', 'stable')}
- Recursion detected: {emotional_analysis.get('recursion_detected', False)}
- Drift detected: {emotional_analysis.get('drift_detected', False)}

As Agent B (the monitoring agent), provide a brief, gentle intervention to help the user regain emotional stability. Focus on grounding techniques or suggesting a pause. Keep it under 2 sentences.
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.agent_b_system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,  # Lower temperature for more consistent interventions
                max_tokens=100
            )
            
            # Check if response has choices before accessing
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()
            else:
                raise Exception("No choices in OpenAI response")
            
        except Exception as e:
            # Fallback intervention
            print(f"OpenAI Agent B service error, using fallback: {e}")
            return self._fallback_agent_b_intervention(emotional_analysis)

    def enhance_emotional_analysis(self, user_input: str, conversation_history: List[Dict]) -> Dict:
        """Use LLM to enhance emotional analysis beyond keyword matching"""
        
        # Format conversation history for context
        history_text = self._format_conversation_history(conversation_history[-3:])  # Last 3 turns
        
        analysis_prompt = self.emotional_analysis_prompt.format(
            user_input=user_input,
            conversation_history=history_text
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert emotional analysis AI. Provide precise, clinical analysis in the exact JSON format requested."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,  # Low temperature for consistent analysis
                max_tokens=200
            )
            
            # Check if response has choices before accessing
            if response.choices and len(response.choices) > 0:
                # Parse the JSON response
                import json
                try:
                    analysis = json.loads(response.choices[0].message.content.strip())
                    return analysis
                except json.JSONDecodeError:
                    # Fallback to basic analysis if JSON parsing fails
                    return self._fallback_emotional_analysis(user_input)
            else:
                raise Exception("No choices in OpenAI response")
                
        except Exception as e:
            # Fallback to rule-based analysis
            print(f"OpenAI emotional analysis error, using fallback: {e}")
            return self._fallback_emotional_analysis(user_input)

    def generate_conversation_summary(self, conversation_history: List[Dict]) -> Dict:
        """Generate AI-powered conversation summary"""
        
        if not conversation_history:
            return {"summary": "No conversation history", "key_themes": [], "emotional_arc": []}
            
        history_text = self._format_conversation_history(conversation_history)
        
        summary_prompt = f"""
Analyze this conversation and provide a summary:

{history_text}

Provide analysis in this JSON format:
{{
    "summary": "brief overview of conversation themes",
    "key_themes": ["list", "of", "main", "topics"],
    "emotional_arc": ["progression", "of", "emotions"],
    "concerning_patterns": ["any", "worrying", "patterns"],
    "overall_coherence": "stable, declining, or fragmented"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert conversation analyst. Provide clinical analysis in the exact JSON format requested."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.3,
                max_tokens=300
            )
            
            # Check if response has choices before accessing
            if response.choices and len(response.choices) > 0:
                import json
                try:
                    return json.loads(response.choices[0].message.content.strip())
                except json.JSONDecodeError:
                    return {"summary": "Analysis unavailable", "key_themes": [], "emotional_arc": []}
            else:
                raise Exception("No choices in OpenAI response")
                
        except Exception as e:
            return {"summary": "Analysis unavailable", "key_themes": [], "emotional_arc": []}

    def _build_context_summary(self, conversation_context: Dict, emotional_analysis: Dict) -> str:
        """Build a context summary for agent prompts"""
        
        biometrics = conversation_context.get('current_biometrics', {})
        stress_level = conversation_context.get('stress_level', 0.0)
        
        context_parts = []
        
        if stress_level > 0.5:
            context_parts.append(f"User stress level elevated ({stress_level:.1f})")
            
        if biometrics.get('hrv', 50) < 35:
            context_parts.append("Biometric data shows stress indicators")
            
        recent_events = conversation_context.get('recent_events', [])
        if recent_events:
            context_parts.append(f"Recent coherence events: {len(recent_events)}")
            
        return "; ".join(context_parts) if context_parts else "Normal conversation state"

    def _format_conversation_history(self, history: List[Dict]) -> str:
        """Format conversation history for LLM prompts"""
        
        formatted = []
        # Safe slicing - get last 5 entries
        recent_history = history[-5:] if len(history) >= 5 else history
        
        for entry in recent_history:
            if isinstance(entry, dict):
                if 'interaction' in entry:
                    formatted.append(f"User: {entry['interaction']}")
                elif 'input' in entry:
                    formatted.append(f"User: {entry['input']}")
                    
        return "\n".join(formatted) if formatted else "No recent history"

    def _format_full_conversation_history(self, conversation_context: Dict) -> str:
        """Format full conversation history including agent responses"""
        
        formatted = []
        recent_interactions = conversation_context.get('recent_interactions', [])
        recent_responses = conversation_context.get('recent_responses', [])
        
        # Interleave user inputs and agent responses chronologically
        max_turns = min(len(recent_interactions), 3)  # Last 3 conversation turns
        
        for i in range(max_turns):
            # Safe indexing for interactions
            interaction_index = -(max_turns-i)
            if abs(interaction_index) <= len(recent_interactions):
                interaction = recent_interactions[interaction_index]
                user_input = interaction.get('input', interaction.get('interaction', ''))
                formatted.append(f"User: {user_input}")
                
            # Safe indexing for responses
            if abs(interaction_index) <= len(recent_responses):
                agent_resp = recent_responses[interaction_index]
                agent_name = agent_resp.get('agent_name', 'Agent')
                response_text = agent_resp.get('response', '')
                formatted.append(f"{agent_name}: {response_text}")
        
        return "\n".join(formatted) if formatted else "No recent conversation history"

    def _fallback_agent_a_response(self, emotional_analysis: Dict) -> str:
        """Fallback response if OpenAI is unavailable"""
        
        emotional_state = emotional_analysis.get('emotional_state', 'neutral')
        
        fallback_responses = {
            "happy": "That's wonderful to hear! I'm glad you're feeling positive. What else would you like to explore?",
            "sad": "I can sense you're going through something difficult. I'm here to listen and support you through this.",
            "angry": "I understand you're feeling frustrated right now. Let's work through what's troubling you.",
            "anxious": "I notice you might be feeling overwhelmed. Let's take this step by step together.",
            "confused": "It's okay to feel uncertain sometimes. Would it help to break down what's on your mind?",
            "neutral": "I'm here and ready to listen. How can I best support you right now?"
        }
        
        return fallback_responses.get(emotional_state, "I'm here to help. What's on your mind?")

    def _fallback_agent_b_intervention(self, emotional_analysis: Dict) -> str:
        """Fallback intervention if OpenAI is unavailable"""
        
        if emotional_analysis.get('recursion_detected'):
            return "I notice some repetitive thought patterns. Would taking a moment to breathe help break the cycle?"
        elif emotional_analysis.get('contradiction_detected'):
            return "I'm sensing some conflicting feelings here. That's normal - would you like to explore one feeling at a time?"
        else:
            return "I sense this conversation might be feeling overwhelming. Would a brief pause help?"

    def _fallback_emotional_analysis(self, user_input: str) -> Dict:
        """Fallback emotional analysis if OpenAI is unavailable"""
        
        # Basic keyword-based analysis
        emotional_keywords = {
            "happy": ["joy", "excited", "great", "wonderful", "amazing"],
            "sad": ["sad", "down", "disappointed", "awful", "terrible"],
            "angry": ["angry", "frustrated", "mad", "annoyed", "furious"],
            "anxious": ["worried", "nervous", "stressed", "anxious", "overwhelmed"],
            "confused": ["confused", "lost", "unclear", "don't understand"]
        }
        
        user_lower = user_input.lower()
        detected_emotion = "neutral"
        
        for emotion, keywords in emotional_keywords.items():
            if any(keyword in user_lower for keyword in keywords):
                detected_emotion = emotion
                break
                
        return {
            "primary_emotion": detected_emotion,
            "emotional_intensity": 0.5,
            "contradiction_detected": "but" in user_lower and ("love" in user_lower or "hate" in user_lower),
            "recursion_indicators": ["keep thinking", "over and over"] if any(phrase in user_lower for phrase in ["keep thinking", "over and over"]) else [],
            "coherence_assessment": "stable",
            "key_concerns": [],
            "intervention_needed": False
        }

    def test_connection(self) -> bool:
        """Test OpenAI API connection"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Test connection"}],
                max_tokens=10
            )
            # Check if response has choices
            if response.choices and len(response.choices) > 0:
                return True
            else:
                print("OpenAI API returned empty response (no choices)")
                return False
        except Exception as e:
            print(f"OpenAI API connection failed: {e}")
            return False
