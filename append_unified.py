import os
import json
import base64
import globals # Ensure globals is known if we import this script? No, this writes to Decoder.py

DECODER_PATH = "Decoder.py"

UNIFIED_CONTENT = r'''

# --- Unified Decoder ---
class UnifiedDecoder:
    def __init__(self):
        self.drivers = []
        self.analysis = {}
        
        # Load Analysis
        try:
            with open('deveui_analysis.json', 'r') as f:
                self.analysis = json.load(f)
        except: pass

        # Load Drivers
        seen = set()
        # globals.COMPATIBILITY is a list of classes
        for cls in globals.COMPATIBILITY:
            if cls not in seen:
                try:
                    inst = cls()
                    self.drivers.append(inst)
                    seen.add(cls)
                except Exception as e:
                    logging.debug(f"Failed to instantiate {cls}: {e}")

    def identify_manufacturer(self, deveui):
        if not deveui: return None
        deveui = deveui.upper().replace(':', '').replace('-', '')
        
        # 1. Look in analysis specific DEVEUI
        if "manufacturers" in self.analysis:
            if deveui in self.analysis["manufacturers"]:
                return self.analysis["manufacturers"][deveui]
                
        # 2. Look in analysis prefixes
        best_match = None
        best_len = 0
        prefixes = self.analysis.get("manufacturers_by_prefix", {})
        for prefix, manuf in prefixes.items():
            if deveui.startswith(prefix):
                if len(prefix) > best_len:
                    best_len = len(prefix)
                    best_match = manuf
        
        if best_match: return best_match

        # 3. Hardcoded Fallbacks
        if deveui.startswith("A84041"): return "dragino"
        if deveui.startswith("24E124"): return "milesight"
        if deveui.startswith("70B3D5E7"): return "watteco"
        if deveui.startswith("70B3D52D"): return "mclimate" 
        
        return None

    def decode_uplink(self, encoded_data, deveui=None):
        # Handle Hex or Base64 or List
        raw_payload = ""
        if isinstance(encoded_data, list):
            raw_payload = "".join([f"{x:02X}" for x in encoded_data])
        elif isinstance(encoded_data, str):
            try:
                # Try base64 first
                b = base64.b64decode(encoded_data)
                raw_payload = b.hex().upper()
            except:
                if len(encoded_data) % 2 == 0:
                   raw_payload = encoded_data.upper()
                else: 
                   return {"error": "Invalid format", "raw": encoded_data}
        
        data_wrapper = {"payload": raw_payload}
        
        manuf = self.identify_manufacturer(deveui)
        
        potential_drivers = self.drivers
        if manuf:
            # Sort to prioritize manufacturer in driver name
            potential_drivers = sorted(self.drivers, key=lambda d: 0 if manuf.lower() in d.name.lower() else 1)
        
        for drv in potential_drivers:
            try:
                d_in = data_wrapper.copy()
                res = drv.parse(d_in, None)
                if res and res.get('parsed'):
                    if len(res['parsed']) > 1: # Ignore empty parses
                        res['parsed']['_driver'] = drv.name
                        return res['parsed']
            except Exception as e:
                pass

        # Fallback for NKE / Nexelec A3... format if no driver matched
        if not decoded and raw_payload.upper().startswith('A3'):
             for d in self.drivers:
                 if 'nexelec' in d.name.lower():
                      try:
                          res = d.parse({"payload": raw_payload}, None)
                          if res and res.get('parsed'): return res['parsed']
                      except: pass
        
        return {"error": "No driver found", "raw": raw_payload, "info": f"Identified Manuf: {manuf}"}

# Global Instance
try:
    unified_decoder = UnifiedDecoder()
except Exception as e:
    logging.error(f"Failed to init UnifiedDecoder: {e}")
    # Fallback mock
    class MockUni:
        def decode_uplink(self, *args): return {"error": "Decoder Init Failed"}
    unified_decoder = MockUni()

'''

with open(DECODER_PATH, "a", encoding="utf-8") as f:
    f.write(UNIFIED_CONTENT)

print("Appended UnifiedDecoder to Decoder.py (renamed variable)")
