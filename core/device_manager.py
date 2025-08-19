import subprocess
import socket
from typing import Dict, Optional
import time




class AppiumServerManager:
    @staticmethod
    def check_server(port: int) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except:
            return False

    @staticmethod
    def restart_server(port: int):
        try:
            subprocess.run(f"kill -9 $(lsof -t -i:{port})", shell=True, timeout=30)
            time.sleep(5)
            subprocess.Popen(
                f"appium --port {port} --relaxed-security",
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            time.sleep(10)
            return True
        except Exception as e:
            print(f"Appium sunucusu yeniden başlatılamadı (port {port}): {str(e)}")
            return False