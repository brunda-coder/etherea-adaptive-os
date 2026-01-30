import sys
import os

# Add root to path
sys.path.append(os.getcwd())

try:
    print("1. Importing Voice Engine...")
    from corund.voice_engine import VoiceEngine

    print("2. Initializing Voice Engine...")
    ve = VoiceEngine()

    print("3. Testing TTS (You should hear 'System Check')...")
    ve.speak("System Check Online")

    print("4. Checking Microphone access...")
    if ve.microphone:
        print("   [OK] Microphone Detected")
    else:
        print("   [FAIL] No Microphone found")

    print("5. Voice Engine Verification Complete.")

except Exception as e:
    print(f"FAILED: {e}")
    import traceback
    traceback.print_exc()
