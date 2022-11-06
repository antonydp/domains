import json, os, sys
import socket
import re
import undetected_chromedriver as uc
from lib import proxytranslate
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 800))  
display.start() 
from selenium import webdriver

options = webdriver.ChromeOptions() 
options.add_argument("start-maximized")
chrome = uc.Chrome(options=options)

if __name__ == '__main__':
    fileJson = 'channels.json'

    with open(fileJson) as f:
        data = json.load(f)

    
    for chann, host in sorted(data.items()):
            chrome.get(host)
            data[chann] = chrome.current_url
            print(chrome.current_url)

    # I write the updated file
    with open(fileJson, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)
