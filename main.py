from config.devices import DEVICES, BROWSER_CONFIGS, XPATHS_OF_APPS 
from core.test_runner import BaseTestRunner
from tests.test_cases import  *

from selenium.webdriver.remote.webdriver import WebDriver
from config.devices import XPATHS_OF_APPS


def main():
    # Configure with custom xpath
    openapp = OpenApp(
        app_xpath=XPATHS_OF_APPS["YouTube"]["uiAutomator"],    ## 
        retry_count=3,
        retry_delay=1,

    )
    


    # test_runner = BaseTestRunner(devices=DEVICES, browser_configs=BROWSER_CONFIGS)
    # test_runner.run_parallel_tests(openapp)

    # connect_wifi= ConnectWifi("GM", xpath=XPATHS_OF_APPS["Wi-Fi"]["xpath"], 
    #                                 wifi_xpath=XPATHS_OF_APPS["Wi-Fi"]["GM_xpath_not_conn"], 
    #                                 connect_button_coords=(989, 2233),
    #                                 wifi_password="E!Pp+cf6wR+*")
    
    # test_runner = BaseTestRunner (devices=DEVICES, browser_configs=BROWSER_CONFIGS)
    # test_runner.run_parallel_tests(connect_wifi)

    # connectwifi = ConnectWifi("GM", xpath=XPATHS_OF_APPS["Wi-Fi"]["xpath"], 
    #                                 wifi_xpath=XPATHS_OF_APPS["Wi-Fi"]["GM_xpath_not_conn"], 
    #                                 connect_button_coords=(989, 2233),
    #                                 wifi_password="E!Pp+cf6wR+*",
    #                                 model_name="Era 50" )
    

    # test_runner = BaseTestRunner(devices=DEVICES, browser_configs=BROWSER_CONFIGS)
    # test_runner.run_parallel_tests(connectwifi)
    
    
    click_power_button = power_button(
        model_name="Era 50"
    )
    starttest_log = StartTest_GetLog(
        testname=click_power_button,
        model_name="Era 50",

    )
    test_runner = BaseTestRunner(devices=DEVICES, browser_configs=BROWSER_CONFIGS)
    test_runner.run_parallel_tests(starttest_log)




    # test_runner = BaseTestRunner(devices=DEVICES, browser_configs=BROWSER_CONFIGS)
    # test_runner.run_parallel_tests(click_power_button)

if __name__ == "__main__":
    main()







