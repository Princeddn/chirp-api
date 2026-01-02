# -*- coding: utf-8 -*-
import sys
import os
import glob
import importlib.util
import json
import re
import base64
from JeedomMocks import Globals  # This triggers the sys.modules injection

class BaseDecoder:
    def identify_and_process_data(self, input_data):
        if isinstance(input_data, str) and re.fullmatch(r"[A-Za-z0-9+/=]+", input_data):
            return base64.b64decode(input_data)
        elif isinstance(input_data, str) and re.fullmatch(r"[0-9a-fA-F]+", input_data):
            return bytes.fromhex(input_data)
        elif isinstance(input_data, (bytes, list, bytearray)):
            return bytes(input_data)
        return b""

    def bytes_to_string(self, input_bytes):
        return ''.join(format(byte, '02x') for byte in input_bytes)

class JeedomDecoder(BaseDecoder):
    def __init__(self, payloads_path="resources/lorapayload/payloads"):
        self.drivers = {}
        self.payloads_path = payloads_path
        self.analysis = {}
        # Pre-load analysis mapping
        self.load_analysis()
        self.load_drivers()

    def load_analysis(self):
        try:
            with open('deveui_analysis.json', 'r', encoding='utf-8') as f:
                self.analysis = json.load(f)
        except:
            self.analysis = {"manufacturers_by_prefix": {}, "models_by_prefix": {}}

    def load_drivers(self):
        print(f"🔌 Loading Jeedom drivers from {self.payloads_path}...")
        py_files = glob.glob(os.path.join(self.payloads_path, "*.py"))
        
        for file_path in py_files:
            filename = os.path.basename(file_path)
            if filename.startswith("__") or filename == "utils.py" or filename == "globals.py":
                continue
            
            module_name = filename[:-3]
            try:
                # Load module dynamically
                spec = importlib.util.spec_from_file_location(module_name, file_path)
                module = importlib.util.module_from_spec(spec)
                
                # We need to capture what is appended to globals.COMPATIBILITY
                start_len = len(Globals.COMPATIBILITY)
                
                sys.modules[module_name] = module
                spec.loader.exec_module(module)
                
                # Check what was added
                end_len = len(Globals.COMPATIBILITY)
                if end_len > start_len:
                    # The last items are the new classes
                    for cls in Globals.COMPATIBILITY[start_len:]:
                        try:
                            instance = cls()
                            driver_name = getattr(instance, 'name', module_name)
                            # Normalize helper: MClimate Wiki -> mclimate_vicki
                            self.drivers[driver_name.lower()] = instance
                            # Also key by filename for direct mapping
                            self.drivers[module_name.lower()] = instance 
                            # print(f"   ✅ Loaded {driver_name}")
                        except Exception as e:
                            print(f"   ⚠️ Failed to instantiate {module_name}: {e}")
            except Exception as e:
                print(f"   ❌ Error loading {filename}: {e}")
        
        print(f"🎉 Loaded {len(self.drivers)} driver instances (including aliases).")

    def find_driver(self, deveui):
        # 1. Try to find model from analysis
        if not deveui: return None, "No DevEUI"
        
        deveui_clean = deveui.upper().replace("-", "").replace(":", "")
        
        # Look for longest matching prefix in models_by_prefix
        best_model = None
        longest_prefix = 0
        
        # This is inefficient 0(N*M), but N (prefixes) is small enough (~500)
        # Optimisation: Check lengths [12..6] specifically
        for length in range(12, 5, -1):
            prefix = deveui_clean[:length]
            if prefix in self.analysis.get("models_by_prefix", {}):
                best_model = self.analysis["models_by_prefix"][prefix]
                break
        
        if best_model:
            # Try to match model name to driver name
            # Model Name: "WS301" -> Driver: "milesight_WS301" matches
            target = best_model.lower().replace("-", "").replace(" ", "")
            
            for d_name, driver in self.drivers.items():
                if target in d_name:
                    return driver, f"Identified {best_model}"
        
        # 2. Manufacturer Only Fallback
        # If we know it's "Milesight", maybe try a generic milesight driver if exists?
        # Not implemented yet.
        
        return None, "Unknown Device"

    def decode_uplink(self, payload, deveui=None):
        payload_bytes = self.identify_and_process_data(payload)
        # Jeedom expects hex string
        payload_hex = self.bytes_to_string(payload_bytes)
        
        driver, info = self.find_driver(deveui)
        
        if driver:
            try:
                # Jeedom format: parse(data={'payload': hex_str}, device=None)
                data_wrapper = {'payload': payload_hex}
                result = driver.parse(data_wrapper, None)
                parsed = result.get('parsed', {})
                if not parsed:
                    return {"raw": payload_hex, "warning": "Driver returned no data", "driver": driver.name}
                
                parsed['_driver'] = driver.name
                parsed['_info'] = info
                return parsed
            except Exception as e:
                return {"error": str(e), "driver": driver.name, "raw": payload_hex}
        
        return {"raw": payload_hex, "error": "No driver identified", "info": info} 

# Singleton for simple import
jeedom_decoder = JeedomDecoder()