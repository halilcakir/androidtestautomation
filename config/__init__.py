"""
Cihaz ve Appium konfigürasyon sabitleri
"""

# Config modüllerini dışa aktar
from .devices import DEVICES, BROWSER_CONFIGS, DEVICE_BUTTON_LOCATIONS

__all__ = ['DEVICES', 'BROWSER_CONFIGS', "DEVICE_BUTTON_LOCATIONS"]