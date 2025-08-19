from appium import webdriver
from appium.options.android import UiAutomator2Options
from multiprocessing import Process
import time
from typing import List, Dict, Optional
from selenium.common.exceptions import WebDriverException
import subprocess
from datetime import datetime
import os
import pandas as pd
import numpy as np
import re

class BaseTestRunner:
    def __init__(self, devices: List[Dict], 
                 browser_configs: List[Dict], 
                 global_timeout: int = 120, 
                 output_dir="C:\\Users\\halil.cakir\\Desktop\\parallel_test\\Logs"):
        
        
        self.devices = devices
        self.browser_configs = browser_configs
        self.global_timeout = global_timeout
        self.output_dir = output_dir

    def run_parallel_tests(self, test_case):
        processes = []
        for device in self.devices:
            process = Process(target=self.run_test, args=(device, test_case))
            process.start()
            processes.append(process)
        
        for process in processes:
            process.join()

    def run_test(self, device: Dict, test_case):
        device_name = device["name"]
        port = device["port"]
        
        try:
            driver = self._initialize_driver(device_name, port)
            if not driver:
                return
                
            try:
                get_temp = AndroidPerformanceMonitor(device_name)
                get_temp.get_thermal_status()
                test_case.run_with_retry(driver, device_name)
                

                self._pull_debug_logs(device_name)
            finally:
                self._safe_quit_driver(driver, device_name)
        except Exception as e:
            print(f"[{device_name}] Test sırasında hata: {str(e)}")

    def _initialize_driver(self, device_name: str, port: int) -> Optional[webdriver.Remote]:
        start_time = time.time()
        
        while time.time() - start_time < self.global_timeout:
            try:
                options = self._get_driver_options(device_name)
                
                # Tarayıcı yapılandırması olmadan doğrudan driver oluştur
                driver = webdriver.Remote(
                    command_executor=f"http://localhost:{port}",
                    options=options
                )
                print(f"[{device_name}] Driver başarıyla başlatıldı (Hiçbir uygulama açılmadı)")
                return driver
                    
            except WebDriverException as e:
                print(f"[{device_name}] Driver başlatma hatası: {str(e)}")
                time.sleep(5)

        print(f"[{device_name}] Driver başlatma zaman aşımına uğradı")
        return None
    
    def _pull_debug_logs(self, device_name: str):
        """Cihazdan debug logger klasörünü çeker"""
        try:
            # Cihazdaki debuglogger klasörünü kontrol et
            check_cmd = f"adb -s {device_name} shell ls /sdcard/debuglogger"
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"[{device_name}] debuglogger klasörü bulunamadı")
                return

            # Klasörü çekmek için hedef dizin oluştur
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            target_dir = os.path.join(self.output_dir, f"{device_name}_{timestamp}")
            os.makedirs(target_dir, exist_ok=True)

            # ADB pull komutu ile logları çek
            pull_cmd = f"adb -s {device_name} pull /sdcard/debuglogger {target_dir}"
            subprocess.run(pull_cmd, shell=True, check=True)
            
            print(f"[{device_name}] debuglogger logları {target_dir} dizinine kopyalandı")
            
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            try:
                with open(f"results_{device_name}.txt", "a", encoding="utf-8") as f:
                    f.write(f"[{device_name}] [{timestamp}] : debuglogger logları {target_dir} dizinine kopyalandı")
            except Exception as e:
                print(f"[{device_name}] ⚠ Failed to write results: {str(e)}")
          

        except subprocess.CalledProcessError as e:
            print(f"[{device_name}] Log çekme hatası: {str(e)}")
        except Exception as e:
            print(f"[{device_name}] Beklenmeyen hata: {str(e)}")


    def _get_driver_options(self, device_name: str) -> UiAutomator2Options:
        options = UiAutomator2Options()
        options.platform_name = "Android"
        options.device_name = device_name
        options.automation_name = "UiAutomator2"
        options.no_reset = False
        options.full_reset = False
        options.new_command_timeout = 300
        options.udid = device_name
        return options

    def _safe_quit_driver(self, driver: webdriver.Remote, device_name: str):
        try:
            if driver:
                driver.quit()
                print(f"[{device_name}] Driver başarıyla kapatıldı")
        except Exception as e:
            print(f"[{device_name}] Driver kapatılırken hata: {str(e)}")
    







class AndroidPerformanceMonitor:
    def __init__(self, device_name: str = None):
        self.device_name = device_name
        self.adb_prefix = f"adb -s {device_name}" if device_name else "adb"

    def _run_adb_command(self, command: str) -> str:
        """Temel ADB komut çalıştırma metodu"""
        try:
            result = subprocess.run(
                f"{self.adb_prefix} {command}",
                shell=True,
                check=True,
                text=True,
                capture_output=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            print(f"ADB command failed: {e.stderr}")
            return ""

    # -------------------- FPS Ölçüm Metodları --------------------
    def get_surfaceflinger_fps(self, package_name: str, duration_sec: int = 5) -> Dict:
        """SurfaceFlinger ile frame zamanlamalarını alır"""
        raw_data = self._run_adb_command(f"shell dumpsys SurfaceFlinger --latency {package_name}")
        frame_times = [line.split() for line in raw_data.strip().split('\n')[1:]]
        
        if not frame_times or len(frame_times[0]) < 3:
            return {"error": "No frame data available"}
        
        timestamps = [int(frame[0]) for frame in frame_times]
        frame_durations = np.diff(timestamps) / 1e6  # nanosaniye -> milisaniye
        
        return {
            "avg_fps": 1000 / np.mean(frame_durations) if frame_durations.size > 0 else 0,
            "janky_frames": np.sum(frame_durations > 16.67),  # 60fps'de 16.67ms/frame
            "frame_data": frame_times
        }

    def get_gfxinfo_fps(self, package_name: str) -> Dict:
        """gfxinfo ile render performans verilerini alır"""
        raw_data = self._run_adb_command(f"shell dumpsys gfxinfo {package_name} framestats")
        
        # Frame timing verilerini parse etme
        frame_stats = [line.split(',') for line in raw_data.split('\n') 
                      if re.match(r'^\d+,', line)]
        
        if not frame_stats:
            return {"error": "No gfxinfo data available"}
        
        df = pd.DataFrame(frame_stats).astype(float)
        percentiles = df.describe(percentiles=[.90, .95])
        
        return {
            "90th_percentile": percentiles.loc["95%"].values[0],
            "95th_percentile": percentiles.loc["95%"].values[0],
            "total_frames": len(frame_stats)
        }

    # -------------------- Sistemsel Metrikler --------------------
    def get_cpu_usage(self, package_name: str) -> Dict:
        """Uygulamanın CPU kullanımını alır"""
        raw_data = self._run_adb_command(f"shell top -n 1 -b | grep {package_name}")
        if not raw_data:
            return {"error": "Process not found"}
        
        parts = re.split(r'\s+', raw_data.strip())
        return {
            "cpu_percent": float(parts[8]),
            "threads": int(parts[9])
        }

    def get_memory_info(self, package_name: str) -> Dict:
        """Detaylı bellek kullanım bilgisi"""
        raw_data = self._run_adb_command(f"shell dumpsys meminfo {package_name}")
        if "No process found" in raw_data:
            return {"error": "Process not found"}
        
        # Örnek parse (gerçek uygulamada daha detaylı parsing gerekir)
        return {
            "pss_kb": self._parse_mem_value(raw_data, "PSS"),
            "private_dirty": self._parse_mem_value(raw_data, "Private Dirty")
        }

    def _parse_mem_value(self, raw_data: str, key: str) -> int:
        """Bellek bilgisi parse helper"""
        match = re.search(rf"{key}:\s*(\d+)", raw_data)
        return int(match.group(1)) if match else 0

    # -------------------- Termal Bilgiler --------------------
    def get_thermal_status(self) -> Dict:
        """Cihazın termal durumunu kontrol eder"""
        raw_data = self._run_adb_command("shell dumpsys thermalservice")
        throttling = "Current throttling status: 1" in raw_data
        temps = re.findall(r"Temperature: (\d+)", raw_data)
        
        return {
            "is_throttling": throttling,
            "temperatures": [int(t) for t in temps]
        }

    # -------------------- Kapsamlı Rapor --------------------
    def get_performance_report(self, package_name: str) -> Dict:
        """Tüm metrikleri içeren kapsamlı rapor"""
        return {
            "fps_metrics": {
                "surfaceflinger": self.get_surfaceflinger_fps(package_name),
                "gfxinfo": self.get_gfxinfo_fps(package_name)
            },
            "system_metrics": {
                "cpu": self.get_cpu_usage(package_name),
                "memory": self.get_memory_info(package_name),
                "thermal": self.get_thermal_status()
            },
            "device_info": self.get_device_info()
        }

    def get_device_info(self) -> Dict:
        """Temel cihaz bilgilerini alır"""
        return {
            "model": self._run_adb_command("shell getprop ro.product.model").strip(),
            "android_version": self._run_adb_command("shell getprop ro.build.version.release").strip()
        }