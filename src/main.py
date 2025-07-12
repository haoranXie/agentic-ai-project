# Contents of /agentic-ai-project/agentic-ai-project/src/main.py

import sys
import time
from typing import Dict, List

# Add colorama for better terminal output
try:
    from colorama import init, Fore, Back, Style
    init()
    COLORS_AVAILABLE = True
except ImportError:
    COLORS_AVAILABLE = False

from agents.specialized_agents import AgentA, AgentB
from core.memory import Memory
from core.reasoning import Reasoning
from utils.config import load_config

class AgenticAISystem:
    """
    Main Agentic AI System implementing emotion-recursive agent loop
    with drift detection and coherence monitoring
    """
    
    def __init__(self):
        self.config = load_config()
        self.memory = Memory()
        self.reasoning = Reasoning()
        
        # Initialize agents with configuration
        agent_a_config = self.config['agent_parameters']['agent_a']
        agent_b_config = self.config['agent_parameters']['agent_b']
        
        self.agent_a = AgentA(
            name=agent_a_config['name'], 
            tone=agent_a_config['tone']
        )
        
        self.agent_b = AgentB(
            name=agent_b_config['name'], 
            tone=agent_b_config['tone']
        )
        
        self.turn_number = 0
        self.demo_mode = self.config.get('simulation', {}).get('demo_mode', False)
        
        # Demo scenarios for testing (3 turns for concise demo)
        self.demo_scenarios = [
            "I'm feeling great today, everything is going well!",
            "Actually, I'm not sure... maybe I'm not feeling that great",
            "Wait... what? I can't focus... my thoughts are all jumbled up and nothing makes sense anymore"
        ]

    def print_colored(self, text: str, color: str = "white", style: str = "normal"):
        """Print colored text if colorama is available"""
        if not COLORS_AVAILABLE:
            print(text)
            return
            
        color_map = {
            "red": Fore.RED,
            "green": Fore.GREEN,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "magenta": Fore.MAGENTA,
            "cyan": Fore.CYAN,
            "white": Fore.WHITE,
            "bright_red": Fore.LIGHTRED_EX,
            "bright_green": Fore.LIGHTGREEN_EX,
            "bright_yellow": Fore.LIGHTYELLOW_EX
        }
        
        style_map = {
            "normal": Style.NORMAL,
            "bright": Style.BRIGHT,
            "dim": Style.DIM
        }
        
        print(f"{style_map.get(style, Style.NORMAL)}{color_map.get(color, Fore.WHITE)}{text}{Style.RESET_ALL}")

    def display_welcome(self):
        """Display welcome message and system info"""
        self.print_colored("\n" + "="*60, "cyan", "bright")
        self.print_colored("COHERENCE PROTOCOL - AGENTIC AI SYSTEM", "cyan", "bright")
        self.print_colored("="*60, "cyan", "bright")
        
        print("\nAssignment: Emotion-Recursive Agent UX + Simulated Drift Loop")
        print("Agents:")
        print(f"   • {self.agent_a.name} (Axis) - Compatibility & Tone Mapper")
        print(f"   • {self.agent_b.name} (M) - Silent Observer & Drift Monitor")
        
        # Show LLM status
        openai_status_a = getattr(self.agent_a, 'llm_available', False)
        openai_status_b = getattr(self.agent_b, 'llm_available', False)
        openai_reasoning = getattr(self.reasoning, 'llm_available', False)
        
        if openai_status_a or openai_status_b or openai_reasoning:
            self.print_colored("AI-POWERED MODE: OpenAI LLM integration active", "bright_green", "bright")
        else:
            self.print_colored("FALLBACK MODE: Using rule-based responses", "yellow", "bright")
        
        if self.demo_mode:
            self.print_colored("\nDEMO MODE ACTIVE - Automated scenario testing", "yellow", "bright")
        else:
            print("\nStart typing to begin conversation...")
            print("Type 'status' for system status, 'demo' for demo mode, 'api' for web interface, 'quit' to exit")
        
        print("\n" + "-"*60)

    def process_user_input(self, user_input: str) -> Dict:
        """Process user input through the reasoning system"""
        self.turn_number += 1
        
        # Analyze input for emotional state and drift patterns
        emotional_analysis = self.reasoning.analyze_input(user_input, self.turn_number)
        
        # Store interaction in memory with biometric simulation
        emotional_intensity = self._calculate_emotional_intensity(emotional_analysis)
        stress_factor = emotional_analysis.get("coherence_status") != "stable"
        
        biometric_data = self.memory.simulate_biometric_response(
            emotional_intensity, 
            stress_factor * 0.5
        )
        
        self.memory.store_interaction(user_input, emotional_analysis, self.turn_number)
        
        return emotional_analysis

    def _calculate_emotional_intensity(self, emotional_analysis: Dict) -> float:
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

    def run_agent_responses(self, user_input: str, emotional_analysis: Dict):
        """Run agent responses with monitoring"""
        memory_context = self.memory.get_conversation_context()
        
        # Agent A responds (always responds)
        response_a = self.agent_a.respond(user_input, emotional_analysis, memory_context)
        self.memory.store_agent_response(self.agent_a.name, response_a, "supportive")
        
        # Agent B monitors and potentially intervenes
        monitoring_result = self.agent_b.monitor_emotional_drift(
            self.memory.get_past_interactions(), 
            emotional_analysis
        )
        
        # Display Agent A response
        self.print_colored(f"\n{self.agent_a.name}: {response_a}", "green")
        
        # Agent B monitoring and alerts
        if monitoring_result.get("alerts_generated"):
            # Agent B outputs alerts directly
            for alert in monitoring_result["alerts_generated"]:
                self.print_colored(f"\n{self.agent_b.name}: {alert}", "bright_red")
        
        # Display biometric alert if needed
        if self.memory.is_biometric_alert():
            biometrics = self.memory.get_current_biometrics()
            self.print_colored(f"\nBIOMETRIC ALERT: HRV: {biometrics['hrv']}, Stress: {biometrics['stress_level']:.1f}", "bright_red")

    def display_system_status(self):
        """Display comprehensive system status"""
        self.print_colored("\n" + "="*50, "magenta")
        self.print_colored("SYSTEM STATUS", "magenta", "bright")
        self.print_colored("="*50, "magenta")
        
        # Memory summary
        memory_summary = self.memory.get_memory_summary()
        print(f"\nMemory:")
        print(f"   • Total Interactions: {memory_summary['total_interactions']}")
        print(f"   • Coherence Events: {memory_summary['coherence_events']}")
        print(f"   • Current Stress Level: {memory_summary['current_stress_level']}")
        print(f"   • Biometric Alert: {'YES' if memory_summary['biometric_alert'] else 'NO'}")
        
        # Agent status
        print(f"\nAgents:")
        agent_a_status = self.agent_a.get_agent_status()
        print(f"   • {agent_a_status['name']}: {agent_a_status['response_count']} responses")
        
        agent_b_status = self.agent_b.get_monitoring_summary()
        print(f"   • {agent_b_status['name']}: {agent_b_status['total_alerts']} alerts generated")
        
        # Conversation summary
        conv_summary = self.reasoning.get_conversation_summary()
        print(f"\nConversation:")
        print(f"   • Total Turns: {conv_summary['total_turns']}")
        print(f"   • Recursion Events: {conv_summary['recursion_count']}")
        print(f"   • Emotional Progression: {' → '.join(conv_summary['emotional_progression'][-5:]) if conv_summary['emotional_progression'] else 'None'}")

    def run_demo_mode(self):
        """Run automated demo with predefined scenarios"""
        self.print_colored("\nDEMO MODE: Testing Emotional Drift Detection", "bright_yellow", "bright")
        self.print_colored("="*60, "yellow")
        
        for i, scenario in enumerate(self.demo_scenarios, 1):
            self.print_colored(f"\nDemo Scenario {i}:", "cyan", "bright")
            self.print_colored(f"You: {scenario}", "white")
            
            # Process the scenario
            emotional_analysis = self.process_user_input(scenario)
            self.run_agent_responses(scenario, emotional_analysis)
            
            # Brief pause between scenarios
            time.sleep(1)
            print("\n" + "-"*40)
        
        self.print_colored("\nDEMO COMPLETE", "bright_green", "bright")
        self.display_system_status()

    def run_interactive_mode(self):
        """Run interactive conversation mode"""
        print("\nInteractive mode started. Type your message:")
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if not user_input:
                    continue
                    
                if user_input.lower() in ['exit', 'quit', 'q']:
                    self.print_colored("\nEnding session. Thank you for testing the system!", "cyan")
                    break
                    
                elif user_input.lower() == 'status':
                    self.display_system_status()
                    continue
                elif user_input.lower() == 'demo':
                    self.run_demo_mode()
                    continue
                    
                elif user_input.lower() == 'api':
                    self.print_colored("\nStarting Web API Server...", "cyan", "bright")
                    print("Open your browser to: http://localhost:5000")
                    print("Press Ctrl+C to stop the server and return to terminal mode")
                    try:
                        from interfaces.api import app
                        app.run(debug=False, host='0.0.0.0', port=5000)
                    except KeyboardInterrupt:
                        self.print_colored("\nReturning to terminal mode...", "cyan")
                        continue
                    except Exception as e:
                        self.print_colored(f"\nAPI Error: {str(e)}", "red")
                    continue
                    
                elif user_input.lower() == 'help':
                    print("\nCommands:")
                    print("   • 'status' - Show system status")
                    print("   • 'demo' - Run demo scenarios")
                    print("   • 'api' - Start web interface")
                    print("   • 'quit' - Exit system")
                    continue
                
                # Process user input
                emotional_analysis = self.process_user_input(user_input)
                self.run_agent_responses(user_input, emotional_analysis)
                
            except Exception as e:
                self.print_colored(f"\nError: {str(e)}", "red")
                print("Please try again or type 'quit' to exit.")

    def run(self):
        """Main execution method"""
        self.display_welcome()
        
        if self.demo_mode:
            self.run_demo_mode()
            
            # Ask if user wants to continue with interactive mode
            try:
                continue_interactive = input("\nContinue with interactive mode? (y/n): ").lower().startswith('y')
                if continue_interactive:
                    self.run_interactive_mode()
            except KeyboardInterrupt:
                pass
        else:
            self.run_interactive_mode()


def main():
    """Main entry point"""
    try:
        system = AgenticAISystem()
        system.run()
    except Exception as e:
        print(f"\nSystem Error: {str(e)}")
        print("Please check your configuration and try again.")
        sys.exit(1)


if __name__ == "__main__":
    main()