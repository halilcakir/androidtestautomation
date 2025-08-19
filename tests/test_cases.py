from abc import ABC, abstractmethod
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from core.test_runner import BaseTestRunner
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions import interaction
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.common.actions.pointer_input import PointerInput
import subprocess
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from config import DEVICE_BUTTON_LOCATIONS
from config.devices import XPATHS_OF_APPS
from config.devices import *
import random
import os
from datetime import datetime

import time

class BaseTest(ABC):
    def __init__(self, retry_count=4, retry_delay=3):
        self.retry_count = retry_count
        self.retry_delay = retry_delay

    @abstractmethod
    def execute(self, driver: WebDriver, device_name: str):
        pass

    def _log_action(self, device_name: str, message: str):
        """Helper method for consistent logging with device context"""

        print(f"[{device_name}] [ACTION] {message}")
        self._write_test_result(device_name," [ACTION]", {message})
    
    def _log_error(self, device_name: str, message: str):
        """Helper method for error logging with device context"""
        print(f"[{device_name}] [ERROR] {message}")
        self._write_test_result(device_name, "Error", message)

        

    def scroll_up(self, driver: WebDriver, device_name: str, 
                 duration_ms=500, ratio_x=0.5, ratio_y=0.8, ratio_end=0.2,
                 random_scroll= False
                 
                 ) -> bool:
        """Enhanced scroll method with better device context handling"""
        self._log_action(device_name, 
                        f"Scrolling up (Y: {ratio_y}→{ratio_end}, Duration: {duration_ms}ms)")
        
        try:
            
            if not random_scroll:
                window_size = driver.get_window_size()
                start_x = window_size['width'] * ratio_x
                start_y = window_size['height'] * ratio_y
                end_y = window_size['height'] * ratio_end

                actions = ActionChains(driver)
                actions.w3c_actions = ActionBuilder(
                    driver, 
                    mouse=PointerInput(interaction.POINTER_TOUCH, "touch")
                )
                actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
                actions.w3c_actions.pointer_action.pointer_down()
                time.sleep(duration_ms / 1000)
                actions.w3c_actions.pointer_action.move_to_location(start_x, end_y)
                actions.w3c_actions.pointer_action.release()
                actions.perform()
            else:
                # Random scroll
                window_size = driver.get_window_size()
                start_x = window_size['width'] * ratio_x
                start_y = window_size['height'] * ratio_y
                end_y = window_size['height'] * ratio_end

                actions = ActionChains(driver)
                actions.w3c_actions = ActionBuilder(
                    driver, 
                    mouse=PointerInput(interaction.POINTER_TOUCH, "touch")
                )
                actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
                actions.w3c_actions.pointer_action.pointer_down()
                time.sleep(duration_ms / 1000)
                actions.w3c_actions.pointer_action.move_to_location(start_x, end_y)
                actions.w3c_actions.pointer_action.release()
                actions.perform()
            
            self._log_action(device_name, "Scroll completed successfully")
            return True
            
        except Exception as e:
            self._log_error(device_name, f"Scroll failed: {str(e)}")
            return False

    def _try_find_and_click(self, driver: WebDriver, device_name: str, 
                          xpath: str, attempt: int) -> bool:
        """Internal method with improved device context handling"""
        self._log_action(device_name, 
                        f"Attempt {attempt}: Locating element @ {xpath}")
        
        try:
            self.find_element(driver,device_name,xpath)
            return True
        

        except Exception as e:
            self._log_error(device_name, f"Element not found: {str(e)}")
            return False

    def find_app(self, driver: WebDriver, device_name: str, xpath: str) -> bool:
        """Enhanced app finding with strategy pattern"""
        strategies = [
            {"name": "Initial attempt", "scroll": False},
            {"name": "Scroll down", "scroll": True, "ratio_y": 0.8, "ratio_end": 0.2},
            {"name": "Alternative scroll", "scroll": True, "ratio_y": 0.5, "ratio_end": 0.3},
            {"name": "Alternative scroll", "scroll": True, "ratio_y": 0.8, "ratio_end": 0.3}
        ]
        
        for i, strategy in enumerate(strategies, 1):
            self._log_action(device_name, f"Strategy {i}: {strategy['name']}")
            time.sleep(0.5)  # Her strateji öncesi bekleme
            
            try:
                # Scroll gerekliyse yap
                if strategy.get('scroll', False):
                    self._log_action(device_name, f"Attempting scroll with params: {strategy}")
                    if not self.scroll_up(driver, device_name,
                                        ratio_y=strategy['ratio_y'],
                                        ratio_end=strategy['ratio_end']):
                        self._log_error(device_name, f"Scroll failed in strategy {i}")
                        continue
                
                # Elementi bul ve tıkla (scroll yapılmayan stratejilerde de çalışır)
                if self._try_find_and_click(driver, device_name, xpath, i):
                    self._log_action(device_name, "App opened successfully")
                    return True
                    
            except Exception as e:
                self._log_error(device_name, f"Strategy {i} failed with error: {str(e)}")
                continue
    
        self._log_error(device_name, "All strategies failed")
        return False




    def _try_find_and_click(self, driver, device_name, xpath, attempt_num) -> bool:
        """Helper method to find and click an element"""
        try:
            self._log_action(device_name, f"Attempt {attempt_num}: Locating element @ {xpath}")
            
            if xpath.strip().startswith("new UiSelector"):
                locator = (AppiumBy.ANDROID_UIAUTOMATOR, xpath)
            else:
                locator = (AppiumBy.XPATH, xpath)
                
            element = WebDriverWait(driver, 5).until(  # Zaman aşımını 5 saniyeye çıkar
                EC.element_to_be_clickable(locator))
            element.click()
            return True
        
        except Exception as e:
            self._log_error(device_name, f"Attempt {attempt_num} failed: {str(e)}")
        return False

    def run_with_retry(self, driver: WebDriver, device_name: str) -> bool:
        """Enhanced retry mechanism with better logging"""
        for attempt in range(1, self.retry_count + 1):
            self._log_action(device_name, 
                            f"Test attempt {attempt}/{self.retry_count}")
            try:
                self.execute(driver, device_name)
                self._write_test_result(device_name, "Success", "Test passed")
                return True
            except Exception as e:
                self._log_error(device_name, 
                               f"Attempt {attempt} failed: {str(e)}")
                if attempt < self.retry_count:
                    time.sleep(self.retry_delay)
        
        self._write_test_result(device_name, "Failure", "All attempts failed")
        return False

    
    
    def _write_test_result(self, device_name: str, test_name: str, result: str):
        """Improved result writing with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        try:
            with open(f"results_{device_name}.txt", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] {test_name}: {result}\n")
        except Exception as e:
            print(f"[{device_name}] ⚠ Failed to write results: {str(e)}")

   
   
   
   
    def find_element(self, driver: WebDriver, device_name: str, xpath: str):
        """Find an element by XPath with improved logging
        
        Args:
        driver (WebDriver): WebDriver instance
        device_name (str): Device name
        xpath (str): Bu alan uygulama bulunacaksa uiAutomator, uygulama içi bir element bulunacaksa xpath olmalıdır.
"""

        try:
            if xpath.strip().startswith("new UiSelector"):
                locator = (AppiumBy.ANDROID_UIAUTOMATOR, xpath)
            else:
                # Varsayılan olarak XPath kabul et
                locator = (AppiumBy.XPATH, xpath)
                
            element = WebDriverWait(driver, 4).until(
                EC.element_to_be_clickable(locator))
            element.click()
            self._log_action(device_name, "Element found and clicked")
            
            if xpath == '//android.widget.Button[@resource-id="android:id/button1"]':
                self._log_action(device_name, "Daha önce kaydedilen log temizlendi.")

        except: 
            self._log_error(device_name, f"Element not found {xpath}")
            if xpath == '//android.widget.Button[@resource-id="android:id/button1"]':
                self._log_action(device_name, f"Daha önce kaydedilen log bulunamadı:")



    def click_main(self, driver, model_name: str,button):
        """Ekranda belirli bir konuma tıklama işlemi
        
        Args:
            driver: Appium WebDriver instance
            model_name: Cihaz model ismi ("Era 50", "Era 30", "GM 24 Pro" gibi)
            button:         "Main_Button": (538, 2385),
                            "Back_Button": (238, 2390),
                            "Apps_Button": (797, 2386),
                            "Clear_All": (552, 1981)
            
        Returns:
            bool: İşlem başarı durumu
            str: Hata mesajı veya başarı bilgisi
            
        Raises:
            ValueError: Geçersiz model adı veya koordinat bulunamazsa
        """
        # Koordinatları dictionary'den al
        device_data = DEVICE_BUTTON_LOCATIONS.get(model_name)
        if not device_data:
            raise ValueError(f"Tanımlı olmayan cihaz modeli: {model_name}")
        
        coords = device_data.get(button)
        if not coords:
            raise ValueError(f"{model_name} modelinde Main_Button koordinatı tanımlı değil")
        
        try:
            # Touch action oluştur ve koordinatları kullan
            actions = ActionChains(driver)
            actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            actions.w3c_actions.pointer_action.move_to_location(coords[0], coords[1])  # coords tuple'ını kullan
            actions.w3c_actions.pointer_action.pointer_down()
            actions.w3c_actions.pointer_action.pause(0.1)
            actions.w3c_actions.pointer_action.release()
            actions.perform()
            
            return True, f"{model_name} cihazında Main_Button'a tıklandı ({coords[0]}, {coords[1]})"
        
        except Exception as e:
            return False, f"{model_name} cihazında tıklama başarısız: {str(e)}"
        
    



    def clear_all_apps(self,driver, model_name: str):
        button_combinations = ["Apps_Button","Clear_All","Main_Button"]
        for i in range(3):
             self.click_main(driver,model_name,button_combinations[i])
             


    
    def perform_swipe(self, driver, start_x, start_y, end_x, end_y, duration):
        """
        Perform a single swipe action
        Args:
            driver: WebDriver instance
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            duration: Duration of the swipe in ms
        """
        try:
            actions = ActionChains(driver)
            actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
            
            # Move to start position
            actions.w3c_actions.pointer_action.move_to_location(start_x, start_y)
            actions.w3c_actions.pointer_action.pointer_down()
            
            # Move to end position
            actions.w3c_actions.pointer_action.move_to_location(end_x, end_y)
            actions.w3c_actions.pointer_action.release()
            
            actions.perform()
            time.sleep(duration/1000)  # Convert ms to seconds
            
            return True
        except Exception as e:
            print(f"Error performing swipe: {str(e)}")
            return False

    def perform_multiple_swipes(self, driver, count=4, **kwargs):
        """
        Perform multiple swipe actions
        Args:
            driver: WebDriver instance
            count: Number of swipes to perform
            kwargs: Arguments for perform_swipe()
        """
        for i in range(count):
            success = self.perform_swipe(driver, **kwargs)
            if not success:
                break
            # Optional: Add variation to coordinates for subsequent swipes
            if i > 0:
                kwargs['start_y'] -= 50
                kwargs['end_y'] -= 50




class OpenApp(BaseTest):
    """Mobil cihazlarda belirtilen bir uygulamayı başlatmayı sağlar.
    Attributes:
        app_xpath (str): Hedef uygulamanın XPATH değeri.
    """

    def __init__(self, app_xpath=None, **kwargs):
        super().__init__(**kwargs)
        self.app_xpath = app_xpath 

    def __call__(self,driver,device_name):
        print("OpenApp is called!")
        self.execute(driver,device_name)

    def execute(self, driver: WebDriver, device_name: str):
        """Main test execution with proper xpath handling"""
        self._log_action(device_name, 
                        f"Starting app test with xpath: {self.app_xpath}")
        time.sleep(1)
        
        self.clear_all_apps(driver,"Era 50")

        time.sleep(2)

        if not self.find_app(driver, device_name, self.app_xpath):
            

            raise Exception("Failed to find and open the app")
        
        
        try:
            if self.app_xpath == XPATHS_OF_APPS["YouTube"]["uiAutomator"]:
            
                    
                notification_allow = WebDriverWait(driver, 3).until(EC.element_to_be_clickable((AppiumBy.XPATH, self.app_xpath)))
                notification_allow.click()

        except:
            self._log_error(device_name, "YouTube için izin verme işlemi başarısız")


        for i in range(25): # 25 scroll 
            try:
                self.scroll_up(driver,device_name,duration_ms=500,ratio_x=0.5,ratio_y=0.8, ratio_end=0.2)
            except:
                break
    
        
        
        
       
        time.sleep(1)

        


class ConnectWifi(BaseTest):
    """
    📶 Mobil cihazlarda Wi-Fi bağlantısı yönetimi 🌐
    
    Bağlanılacak Wi-Fi ağını bulur ve bağlantı kurar.
    
    🔧 Kullanım Örneği:
    ==================
    
    >>> wifi = ConnectWifi(
    ...     wifi_name='Ev_Wifi_5G',
    ...     settings_xpath='//*[@text="Wi-Fi"]',
    ...     wifi_list_xpath='//android.widget.TextView',
    ...     connect_button_coords=(989, 2233)
    ... )
    
    📌 Parametreler:
    ================
    
    Args:
        wifi_name (str): Bağlanılacak ağın SSID'si (örn: "Ev_Wifi")
        settings_xpath (str): Ayarlar > Wi-Fi yolunun XPath'i
        wifi_list_xpath (str): Ağ listesindeki öğelerin XPath'i
        connect_button_coords (tuple): (x,y) formatında dokunma koordinatları
    
    ⚠️  DİKKAT: 
    ===========
    Koordinatlar cihaz çözünürlüğüne göre değişir!
    
    Examples:
        >>> # Temel kullanım
        >>> wifi_manager = ConnectWifi(
        ...     wifi_name="OfisWifi",
        ...     settings_xpath='//*[@text="Wi-Fi"]',
        ...     wifi_list_xpath='//android.widget.TextView',
        ...     connect_button_coords=(500, 1200)
        ... )
        
        >>> # Farklı cihaz için koordinat ayarı
        >>> wifi_tablet = ConnectWifi(
        ...     wifi_name="Ev_Wifi_2.4G",
        ...     settings_xpath='//*[@resource-id="com.android.settings:id/wifi"]',
        ...     wifi_list_xpath='//android.widget.LinearLayout',
        ...     connect_button_coords=(1200, 800)
        ... )
    
    Note:
        Bu class Android cihazlar için tasarlanmıştır ve UI otomasyonu 
        araçları (Appium, UIAutomator vb.) ile birlikte kullanılır.
    """

    def __init__(self, wifi_name=None, 
                 wifi_password=None, 
                 xpath=None, 
                 wifi_xpath=None,
                 model_name: str = None,
                 connect_button_coords=(989, 2233),
                 **kwargs):
     
        self.wifi_xpath = wifi_xpath
        self.wifi_name = wifi_name
        self.wifi_password = wifi_password 
        self.xpath = xpath
        self.connect_button_coords = connect_button_coords
        self.model_name = model_name

        
        super().__init__(**kwargs)

    def _enter_wifi_password(self, driver):
        """WiFi şifresini girer ve bağlan butonuna tıklar"""
        try:
            # Şifre alanını bul ve şifreyi gir
            password_field = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((AppiumBy.ID, "com.android.settings:id/password"))
            )
            password_field.click()
            password_field.clear()
            password_field.send_keys(self.wifi_password)
            
            # Bağlan butonuna tıkla (koordinat bazlı)
            self._click_at_coordinates(driver, *self.connect_button_coords)
            
            return True, "WiFi şifresi başarıyla girildi ve bağlanıldı"
        except Exception as e:
            return False, f"WiFi şifre girişi başarısız: {str(e)}"

    def _click_at_coordinates(self, driver, x, y, duration=0.1):
        """Belirtilen koordinatlara tıklama işlemi yapar"""
        actions = ActionChains(driver)
        actions.w3c_actions = ActionBuilder(driver, mouse=PointerInput(interaction.POINTER_TOUCH, "touch"))
        actions.w3c_actions.pointer_action.move_to_location(x, y)
        actions.w3c_actions.pointer_action.pointer_down()
        actions.w3c_actions.pointer_action.pause(duration)
        actions.w3c_actions.pointer_action.release()
        actions.perform()

    def execute(self, driver, device_name):
        """WiFi bağlantı işlemini gerçekleştirir"""
        results = []
        self.clear_all_apps(driver,"Era 50")
        try:
            # Adım 1: Ayarlar uygulamasını aç (sadece bir kez kontrol et)
            settings = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//android.widget.TextView[@text="Settings"]'))
            )
            settings.click()
            results.append((True, "Ayarlar açıldı"))
            time.sleep(1)
            
            # Adım 2: WiFi menüsüne git
            wifi_menu = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, self.xpath))
            )
            wifi_menu.click()
            results.append((True, "WiFi menüsü açıldı"))
            time.sleep(1)
            
            # Adım 3: Belirtilen WiFi ağını seç
            wifi_network = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, self.wifi_xpath))
            )
            wifi_network.click()
            results.append((True, "WiFi ağı seçildi"))
            time.sleep(1)
            
            # Adım 4: Şifreyi gir ve bağlan
            result, message = self._enter_wifi_password(driver)
            results.append((result, message))
            
            # Tüm adımların sonucunu değerlendir
            success = all([r[0] for r in results])
            detailed_message = " | ".join([r[1] for r in results])
            
            return success, detailed_message
            
        except Exception as e:
            return False, f"WiFi bağlantı işlemi başarısız: {str(e)}"
        





class StartTest_GetLog(BaseTest):

    """Oluşturulan senaryaolar gerçekleştirilir.
    Testler , senaryoların başarıyla tamamlanması ve logların doğru kaydedilmesi temel alınır.

    Args:
    testname: Testin adı test_case.py dosyasında.
    record_loc: Testin kaydedileceği lokasyon. (Debuglogger)

    """


    def __init__(self, testname:callable, model_name: str,**kwargs)->None:
        self.testname = testname
        self.model_name = model_name
        super().__init__(**kwargs)


    # Log Kaydını Başlat    
    def _start_log(self, driver, device_name):

        self.clear_all_apps(driver,self.model_name)
        time.sleep(2)
        try:
            self.find_app(driver,device_name,'//android.widget.TextView[@content-desc="Phone"]')
            time.sleep(0.5)
            self.find_app(driver,device_name,'//android.widget.ImageButton[@content-desc="key pad"]')
            time.sleep(0.5)
            keypad = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.google.android.dialer:id/digits"]')))
            keypad.send_keys(KEYCODES["Log_Screen"])
            time.sleep(0.5)

            permissions = [
                ("Record_Video", 1),  # Tuple of (permission_name, timeout)
                ("Location", 1),
                ("Nearby_Devices", 1),
                ("Phone_Calls", 1)
            ]

            max_wait_time = 5  # İzinlerin çıkması için maksimum bekleme süresi
            start_time = time.time()

            while time.time() - start_time < max_wait_time:
                found_permission = False
                
                for permission, timeout in permissions:
                    try:
                        permission_xpath = XPATHS_OF_PERMISSIONS.get(permission)
                        if not permission_xpath:
                            continue
                            
                        # Daha kısa bir timeout ile elementin çıkıp çıkmadığını kontrol et
                        allow_btn = WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable((AppiumBy.XPATH, permission_xpath)))
                        allow_btn.click()
                        self._log_action(device_name, f"Allowed {permission} permission")
                        time.sleep(0.5)
                        found_permission = True
                        
                        # İşlenen izini listeden çıkar (opsiyonel)
                        permissions = [(p, t) for p, t in permissions if p != permission]
                        break  # Yeni bir döngüye başla
                        
                    except Exception as e:
                        continue  # Bu izin şu an görünür değil, diğerlerini kontrol et
                
                if not found_permission:
                    # Hiçbir izin bulunamadıysa kısa bir bekle
                    time.sleep(0.5)

            # Kalan izinler için hata loglama
            for permission, _ in permissions:
                print(device_name, {permission}, "Bulunamadı.")
                self._log_error(device_name, f"{permission} İzin bulunamadı.")


            swipe_params = {
                'start_x': 950,
                'start_y': 1200,
                'end_x': 100,
                'end_y': 1200,
                'duration': 250
            }

            self.perform_multiple_swipes(driver, count=4, **swipe_params)
            time.sleep(0.5)
            self.find_element(driver,device_name,'//android.widget.TextView[@resource-id="android:id/title" and @text="DebugLoggerUI"]')
            
            if self.clear_logs(driver,device_name):

                xpath_start_log = '//android.widget.ToggleButton[@resource-id="com.debug.loggerui:id/startStopToggleButton"]'
                            
                self.find_element(driver, device_name,xpath_start_log)
                time.sleep(5)
                
        except:
            pass



    # Logu başlattıktan sonra, logun kaydedildiği yer
    def _end_log(self, driver,device_name):
        self.clear_all_apps(driver,self.model_name)
        time.sleep(2)
        try:
            self.find_app(driver,device_name,'//android.widget.TextView[@content-desc="Phone"]')
            time.sleep(0.5)
            self.find_app(driver,device_name,'//android.widget.ImageButton[@content-desc="key pad"]')
            time.sleep(0.5)
            keypad = WebDriverWait(driver, 1).until(EC.element_to_be_clickable((AppiumBy.XPATH, '//android.widget.EditText[@resource-id="com.google.android.dialer:id/digits"]')))
            keypad.send_keys(KEYCODES["Log_Screen"])
            time.sleep(0.5)
            swipe_params = {
                'start_x': 950,
                'start_y': 1200,
                'end_x': 100,
                'end_y': 1200,
                'duration': 250
            }
            self.perform_multiple_swipes(driver, count=4, **swipe_params)
            time.sleep(0.5)
            self.find_element(driver,device_name,'//android.widget.TextView[@resource-id="android:id/title" and @text="DebugLoggerUI"]')
            xpath_start_log = '//android.widget.ToggleButton[@resource-id="com.debug.loggerui:id/startStopToggleButton"]'     
            self.find_element(driver, device_name,xpath_start_log)

        except: 
            self._log_error("Log sonlandırılamadı.")
            self._log_action(device_name,"Log sonlandırılamadı.")

        pass


    def clear_logs(self, driver, device_name):
        """Logları temizleme işlemini yöneten fonksiyon"""
        try:
            # Tüm gerekli elementlerin bulunup bulunmadığını kontrol et
            self.find_element(driver, device_name, '//android.widget.ImageButton[@resource-id="com.debug.loggerui:id/clearLogImageButton"]')
            self.find_element(driver, device_name, '//android.widget.Button[@text="CLEAR ALL"]')
            self.find_element(driver, device_name, '//android.widget.Button[@resource-id="android:id/button1"]')

            return True
            
        except Exception as e:
            self._log_action(device_name, f"Daha önce kaydedilmiş log bulunmadı: {str(e)}")
            return False

    def wake_screen_up(self,duration:float):
        time.sleep(duration)



    def execute(self, driver, device_name:str):
        try:

            self.wake_screen_up(1.0) 

            # Log kaydını başlat
            self._start_log(driver,device_name)

            self.click_main(driver,self.model_name,"Main_Button")
            # Testi çalıştır
            self.testname(driver,device_name)
            # Log kaydını sonlandır
            self._end_log(driver,device_name)

            return True, "Test başarıyla tamamlandı."
        
        except Exception as e:

            self._log_error(device_name, message=e)
            
            return False, "Test başarısız."

  

class power_button(BaseTest):

    def __init__(self, model_name: str, **kwargs, ):
        self.model_name = model_name
        super().__init__(**kwargs)
    
    
    def __call__(self,driver,device_name):
        print("Power button is called!")
        self.execute(driver,device_name)


    def execute(self, driver, device_name: str):
        try: 
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            folder_name = f"{device_name}_{timestamp}"
            os.makedirs(folder_name, exist_ok=True)

            for i in range(20):
                subprocess.run(f"adb -s {device_name} shell screencap -p /sdcard/{i}ö.png", shell=True)
                time.sleep(0.1)
                subprocess.run(f"adb -s {device_name} pull /sdcard/{i}ö.png {folder_name}/{i}ö.png", shell=True)
                time.sleep(0.1)
                subprocess.run(f"adb -s {device_name} shell input keyevent 26", shell=True)
                time.sleep(0.5)
                subprocess.run(f"adb -s {device_name} shell screencap -p /sdcard/{i}s.png", shell=True)
                time.sleep(0.1)
                subprocess.run(f"adb -s {device_name} pull /sdcard/{i}s.png {folder_name}/{i}s.png", shell=True)
                time.sleep(0.1)
                self._log_action(device_name, f"Power button clicked {i} times")

            return True, "Power button clicked"
        except Exception as e:
            return False, f"Power button click failed: {str(e)}"
