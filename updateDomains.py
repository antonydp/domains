import json, os, sys
import socket
import re
import undetected_chromedriver as uc
from lib import proxytranslate
from pyvirtualdisplay import Display
from selenium import webdriver

if __name__ == '__main__':
    
    display = Display(visible=0, size=(800, 800))  
    display.start() 
    driver = uc.Chrome()
    fileJson = 'channels.json'

    with open(fileJson) as f:
        data = json.load(f)

    for chann, host in sorted(data.items()):
        driver.get(host)
        data[chann] = driver.current_url
        print(driver.current_url)

    # I write the updated file
    with open(fileJson, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)
