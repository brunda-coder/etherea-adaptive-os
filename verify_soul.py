from corund.ui.avatar_heroine_widget import AvatarHeroineWidget, EI
from corund.state import AppState
from PySide6.QtWidgets import QApplication
import sys
import time

def verify_vivid_motion():
    app = QApplication(sys.argv)
    state = AppState.instance()
    avatar = AvatarHeroineWidget()
    
    print("--- VIVID MOTION ENGINE VERIFICATION ---")
    
    # Test 1: Idle Movement
    print("\n[TEST 1] Idle Mode (Breathing Only)")
    state.set_expressive_mode("idle")
    avatar._tick() # Simulate one tick
    t0 = avatar.t
    sway0 = avatar._dance_sway
    print(f"Start T: {t0:.2f}, Sway: {sway0:.2f}")
    
    # Test 2: Dance Movement
    print("\n[TEST 2] Dance Mode (Swaying)")
    state.set_expressive_mode("dance")
    
    for i in range(10):
        time.sleep(0.03) # Simulate real time delay
        avatar._tick()
        print(f"Step {i} | T: {avatar.t:.2f} | Sway: {avatar._dance_sway:.2f} | Bob: {avatar._dance_bob:.2f}")
    
    final_sway = abs(avatar._dance_sway)
    if final_sway > 0.1:
        print("\n✅ SUCCESS: Motion detected. Sway amplitude is active.")
    else:
        print("\n❌ FAILURE: No motion detected.")

    # Test 3: Language Sync
    print("\n[TEST 3] State Persistence")
    state.set_expressive_mode("humming")
    avatar._tick()
    print(f"Mode Check: {avatar.expressive_mode} (Expected: humming)")
    
    if avatar.expressive_mode == "humming":
        print("✅ SUCCESS: AppState -> Avatar sync verified.")
    else:
        print("❌ FAILURE: AppState sync failed.")

if __name__ == "__main__":
    verify_vivid_motion()
