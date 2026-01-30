import os
import json
from corund.tools.router import ToolRouter
from corund.agent import IntelligentAgent
from corund.voice import VoiceEngine
from corund.state import AppState

def run_verification():
    print("--- ETHEREA AGENTIC VERIFICATION ---")
    router = ToolRouter.instance()
    agent = IntelligentAgent()
    state = AppState.instance()

    # 1. Test NEXT 1 (Tool Contract & Safety)
    print("\n[Test 1] Tool Contract & Safety")
    list_res = router.list_dir(".", depth=1)
    print(f"LIST results: {len(list_res.get('files', []))} files found.")
    
    safe_write = router.write_file("logs/test.txt", "Verification pass.")
    print(f"Safe Write (Project Root): {safe_write['success']}")
    
    unsafe_write = router.write_file("../unsafe.txt", "Hacked.")
    print(f"Unsafe Write (Outside Root): {unsafe_write.get('success')} (Error: {unsafe_write.get('error')})")

    # 2. Test NEXT 3 (Vocal Routing)
    print("\n[Test 2] Vocal Routing (Kannada/Hindi)")
    voice = VoiceEngine.instance()
    voice.speak("ನಮಸ್ಕಾರ, ನಾನು ಎಥೇರಿಯಾ.") # Kannada
    print("Vocal queue updated with Kannada.")

    # 3. Test NEXT 2 (Agent Loop)
    print("\n[Test 3] Agent Loop Execution")
    # We'll mock a task execution
    agent.execute_task("summarize README.md")
    print("Agent task started.")

    # 4. Check Logs (NEXT 1)
    log_file = os.path.join(os.getcwd(), "logs", "tool_calls.jsonl")
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            logs = f.readlines()
            print(f"Audit Log Check: {len(logs)} calls recorded.")

    print("\n--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    run_verification()
