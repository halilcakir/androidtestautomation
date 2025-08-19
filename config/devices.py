DEVICES = [
  
    # {"name": "L2885900151", "port": 4725},
    {"name": "L2904200592", "port": 4724},
    {"name": "L2897100765", "port": 4723},
   
    # {"name": "L2885900175", "port": 4726},
   
]

BROWSER_CONFIGS = [
    {
        "name": "Android Home", 
        "package": "com.android.launcher3",  # Çoğu Android cihazda ana ekran paketi
        "activity": "com.android.launcher3.Launcher"
    }
]

DEVICE_BUTTON_LOCATIONS = {

    "Era 50": {
        "Main_Button": (538, 2385),
        "Back_Button": (238, 2390),         
        "Apps_Button": (797, 2386),
        "Clear_All": (552, 1981)
    }
}

XPATHS_OF_APPS = {
    "Instagram":{
        "": '//android.widget.TextView[@text="Instagram"]',
            },

    "YouTube": {
        "uiAutomator": 'new UiSelector().text("YouTube")',
        
    },

    "Chrome": {
        "xpath": '//android.widget.TextView[@content-desc="Chrome"]',
    
    },

    "Settings": {
        "xpath": [
            '//android.widget.TextView[@text="Settings"]',  # Çoğu cihaz
            '//android.widget.TextView[@content-desc="Settings"]',  # Bazı cihazlar
            '//android.widget.TextView[contains(@text, "Ayarlar")]',  # Türkçe cihazlar
            '//android.widget.TextView[contains(@content-desc, "Ayarlar")]'  # Türkçe alternatif
        ],
        "activity": "com.android.settings/.Settings",  # ADB ile açmak için
        "package": "com.android.settings"  # Appium ile açmak için
    },
    "Wi-Fi":{
        "xpath": '(//android.widget.RelativeLayout[@resource-id="com.android.settings:id/text_frame"])[1]',
        "switch": '//android.widget.Switch[@resource-id="android:id/switch_widget"]',
        "GM_xpath_not_conn": '//android.widget.LinearLayout[@content-desc="gm,Wifi signal full.,Secure network"]/android.widget.LinearLayout[1]/android.widget.RelativeLayout',
        "GM_xpath_conn": '//android.widget.LinearLayout[@content-desc="gm,Connected,Wifi signal full.,Secure network"]/android.widget.LinearLayout[1]/android.widget.RelativeLayout'
    }
    
}

KEYCODES = {
    "Log_Screen": '*#*#8803#*#*',
    "Info": '*#*#8801#*#*'
}



XPATHS_OF_PERMISSIONS = {
    "Record_Video" : '//android.widget.Button[@resource-id="com.android.permissioncontroller:id/permission_allow_foreground_only_button"]',
    "Location" : '//android.widget.Button[@resource-id="com.android.permissioncontroller:id/permission_allow_foreground_only_button"]',
    "Nearby_Devices": '//android.widget.Button[@resource-id="com.android.permissioncontroller:id/permission_allow_button"]',
    "Phone_Calls" : '//android.widget.Button[@resource-id="com.android.permissioncontroller:id/permission_allow_button"]',
}