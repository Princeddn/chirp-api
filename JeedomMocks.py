import sys
import logging

# --- Mock Utils ---
class Utils:
    @staticmethod
    def hexarray_from_string(hex_str):
        # Converts "0A0B" to [10, 11]
        try:
            return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]
        except:
            return []

# --- Mock Globals ---
class Globals:
    COMPATIBILITY = []

# --- Custom Logger ---
# Redirect Jeedom logging to standard python logging
console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
logger = logging.getLogger("JeedomShim")
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)

# Register Mocks in sys.modules so plugins can "import utils" or "import globals"
import types

m_utils = types.ModuleType('utils')
m_utils.hexarray_from_string = Utils.hexarray_from_string
sys.modules['utils'] = m_utils

m_globals = types.ModuleType('globals')
m_globals.COMPATIBILITY = Globals.COMPATIBILITY
sys.modules['globals'] = m_globals
