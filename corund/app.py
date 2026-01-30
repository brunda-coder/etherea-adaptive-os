import sys
import argparse
import math
import time
import random

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

from corund.state import AppState
from corund.ui.main_window import HeroMainWindow

def run_demo_simulation():
    """
    Deterministic EI simulation for demo purposes.
    Oscillates focus/stress/energy based on time.
    """
    state = AppState.instance()
    t = time.time()
    
    # Deterministic Sine Waves
    # Focus: Smooth cycle 0.2 -> 0.9
    focus = 0.55 + 0.35 * math.sin(t * 0.5)
    
    # Stress: Rises with focus, drops in break
    # We'll just simulate a complex wave
    stress = 0.3 + 0.2 * math.sin(t * 0.2) + 0.1 * math.cos(t * 0.8)
    
    # Energy: Slow decay + recovery
    energy = 0.6 + 0.3 * math.sin(t * 0.1)
    
    # Curiosity: Random drift
    curiosity = 0.5 + 0.2 * math.sin(t * 0.3)

    state.update_ei(
        focus=focus,
        stress=stress,
        energy=energy,
        curiosity=curiosity
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--demo", action="store_true", help="Run in Hero Demo mode with simulated EI")
    args = parser.parse_args()

    app = QApplication(sys.argv)
    
    # Setup Main Window
    window = HeroMainWindow()
    window.show()

    # Demo Mode Logic
    if args.demo:
        print("🌟 Etherea Hero Demo Started")
        print("   - Deterministic EI Simulation: ON")
        print("   - Sensors: BYPASSED")
        
        # 10Hz EI update loop
        demo_timer = QTimer()
        demo_timer.timeout.connect(run_demo_simulation)
        demo_timer.start(100)
        
        # KEEP REFERENCE to prevent GC
        window._demo_timer_ref = demo_timer 

    else:
        # 🌟 Normal Mode: Living OS
        print("Etherea Living OS Activated")
        from corund.senses import InputSenses
        from corund.state import AppState
        
        from corund.signals import signals
        
        state = AppState.instance()
        senses = InputSenses()
        
        # Connect Senses -> System
        senses.activity_level_changed.connect(lambda level: state.update_ei(energy=0.3 + level * 0.7))
        senses.pattern_detected.connect(signals.pattern_detected.emit)
        senses.start()
        
        # Keep ref
        window._senses_ref = senses

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
