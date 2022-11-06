import json, os, sys
import socket
import re
from lib import proxytranslate
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import chromedriver_autoinstaller
from pyvirtualdisplay import Display
display = Display(visible=0, size=(800, 800))  
display.start()

chromedriver_autoinstaller.install()  # Check if the current version of chromedriver exists
                                      # and if it doesn't exist, download it automatically,
                                      # then add chromedriver to path

chrome_options = webdriver.ChromeOptions()    
# Add your options as needed    
options = [
  # Define window size here
   "--window-size=1200,1200",
    "--ignore-certificate-errors"
 
    #"--headless",
    #"--disable-gpu",
    #"--window-size=1920,1200",
    #"--ignore-certificate-errors",
    #"--disable-extensions",
    #"--no-sandbox",
    #"--disable-dev-shm-usage",
    #'--remote-debugging-port=9222'
]

for option in options:
    chrome_options.add_argument(option)

    
driver = webdriver.Chrome(options = chrome_options)

                
path = os.getcwd()
sys.path.insert(0, path)
if sys.version_info[0] >= 3:
    from lib import py3 as httplib2
else:
    from lib import py2 as httplib2


def http_Resp(lst_urls):
    rslt = {}
    for sito in lst_urls:
        try:
            s = httplib2.Http()
            code, resp = s.request(sito, body=None)
            if code.previous:
                rslt['code'] = code.previous['status']
                rslt['redirect'] = code.previous.get("location")
                rslt['status'] = code.status
                print("r1 http_Resp: %s %s %s %s" %
                      (code.status, code.reason, rslt['code'], rslt['redirect']))
            else:
                rslt['code'] = code.status
        except httplib2.ServerNotFoundError as msg:
            # both for lack of ADSL and for non-existent sites
            rslt['code'] = -2
        except socket.error as msg:
            # for unreachable sites without correct DNS
            # [Errno 111] Connection refused
            rslt['code'] = 111
        except:
            print()
            rslt['code'] = 'Connection error'
    return rslt


if __name__ == '__main__':
    fileJson = 'channels.json'

    with open(fileJson) as f:
        data = json.load(f)

    
    for chann, host in sorted(data.items()):
            # to get an idea of the timing
            # useful only if you control all channels
            # for channels with error 522 about 40 seconds are lost ...
            print("check #### INIZIO #### channel - host :%s - %s " % (chann, host))

            rslt = http_Resp([host])

            # all right
            if rslt['code'] == 200:
                data[chann] = host
            # redirect
            elif str(rslt['code']).startswith('3'):
                # data[k][chann] = str(rslt['code']) +' - '+ rslt['redirect'][:-1]
                data[chann] = rslt['redirect']
            # cloudflare...
            elif rslt['code'] in [429, 503, 403]:
                print('Cloudflare riconosciuto')
                try:
                    a = re.search('<base href="([^"]+)', proxytranslate.process_request_proxy(host).get('data', '')).group(1)
                    print("dw" + a)
                    page_data = proxytranslate.process_request_proxy(host).get('data', '')
                    data[chann] = re.search('<base href="([^"]+)', page_data).group(1)
                    rslt['code_new'] = 200
                except Exception as e:
                    import traceback
                    traceback.print_exc()
            # non-existent site
            elif rslt['code'] == -2:
                print('Host Sconosciuto - '+ str(rslt['code']) +' - '+ host)
            # site not reachable
            elif rslt['code'] == 111:
                driver.get(host)
                data[chann] = driver.current_url
            else:
                # other types of errors
                print('Errore Sconosciuto - '+str(rslt['code']) +' - '+ host)

            print("check #### FINE #### rslt :%s  " % (rslt))
            print(data[chann])
            if data[chann].endswith('/'):
                data[chann] = data[chann][:-1]

    # I write the updated file
    with open(fileJson, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)
