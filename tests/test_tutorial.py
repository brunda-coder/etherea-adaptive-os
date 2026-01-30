import sys
import os
sys.path.append(os.getcwd())

from corund.tutorial_flow import TutorialFlow
from corund.avatar_engine import AvatarEngine
import unittest.mock

# Mock AvatarEngine to avoid API key error
AvatarEngine._get_api_key = lambda self, p=None: "dummy-key"

def test_tutorial_triggers():
    print("Testing Tutorial Triggers...")
    flow = TutorialFlow()
    
    # Test 1: First Launch
    context = {"startup": True}
    msg = flow.check_triggers(context)
    if msg and "Welcome" in msg:
        print("PASS: First launch trigger working.")
    else:
        print(f"FAIL: First launch trigger returned: {msg}")

    # Test 2: High Stress
    context = {"stress": 0.9}
    msg = flow.check_triggers(context)
    if msg and "stress" in msg:
        print("PASS: Stress trigger working.")
    else:
        print(f"FAIL: Stress trigger returned: {msg}")

    # Test 3: No Trigger
    context = {"stress": 0.1}
    msg = flow.check_triggers(context)
    if msg is None:
        print("PASS: No trigger for normal state.")
    else:
        print(f"FAIL: Unexpected trigger: {msg}")

if __name__ == "__main__":
    test_tutorial_triggers()
