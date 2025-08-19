import logging
from datetime import datetime
import os

def take_screenshot(driver, device_name, prefix="screenshot"):
    """Ekran görüntüsü alır"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{prefix}_{device_name}_{timestamp}.png"
    driver.save_screenshot(filename)
    return filename

def generate_report(test_results, filename="test_report.json"):
    """Test raporu oluşturur"""
    import json
    with open(filename, 'w') as f:
        json.dump(test_results, f, indent=2)

def setup_logger(name):
    """Log mekanizması kurar"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger