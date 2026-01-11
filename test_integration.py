import sys
import os
import json

# Ensure we can import from the current directory
sys.path.append(os.getcwd())

try:
    print("Attempting to import Decoder...")
    from Decoder import jeedom_decoder
    print("Successfully imported jeedom_decoder.")
    
    # Simple test payload (empty or generic) to ensure no crash on calling
    print("Attempting a test decode...")
    # Using a dummy payload and generic DevEUI
    res = jeedom_decoder.decode_uplink("00", "0000000000000000")
    print(f"Decode result: {res}")
    
    print("Integration test PASSED.")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)
except Exception as e:
    print(f"RuntimeError: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
