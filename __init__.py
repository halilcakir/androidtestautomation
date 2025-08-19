"""
Appium Test Framework - Ana Paket
"""

# Versiyon bilgisi
__version__ = "1.0.0"

# Kullanıcıya açık API'ler
from .core.test_runner import BaseTestRunner
from core import device_manager

# İstenirse tüm modülleri otomatik yükleyebilir
__all__ = ['BaseTestRunner', 'device_manager']

# Paket yüklendiğinde çalışacak başlatma kodu (opsiyonel)
print(f"{__name__} v{__version__} başlatıldı")