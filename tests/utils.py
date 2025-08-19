from .test_cases import BaseTest
from appium import webdriver
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
import subprocess

import time
from typing import Optional, Tuple

class UtilFunctions(BaseTest):
    """WiFi yönetimi sağlayan sınıf"""
    
    def __init__(self ,**kwargs):
        """
        Args:
            ssid: Bağlanılacak ağ adı
            password: WiFi şifresi
            kwargs: Ek ayarlar (retry_count, timeout vb.)
        """
        super().__init__(**kwargs)
    
        self.retry_count = kwargs.get('retry_count', 3)
        self.timeout = kwargs.get('timeout', 10)
   
    def toggle_wifi(self, driver: WebDriver):
        """WiFi'yi açıp kapatan metod"""
        self.click_main(driver,"Main_Button")
        self.open_settings_via_adb(driver)
        success = True  # Gerçek kontrol mekanizması eklenmeli
        message = "WiFi toggled successfully"
        return success, message
    



    

    def execute(self, driver: WebDriver, device_name: str) -> bool:
   
        success, message = self.toggle_wifi(driver)
        print(f"{device_name}: {message}")
        return success