import undetected_chromedriver as uc
import time 
from pyvirtualdisplay import Display 
import json, os, sys
import socket

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
    display = Display(visible=0, size=(800, 800))  
    display.start()  
    driver = uc.Chrome() 
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
            else:
                # other types of errors
                driver.get(host)
                time.sleep(7)
                data[chann] = driver.current_url

            print("check #### FINE #### rslt :%s  " % (rslt))
            if data[chann].endswith('/'):
                data[chann] = data[chann][:-1]

    # I write the updated file
    with open(fileJson, 'w') as f:
        json.dump(data, f, sort_keys=True, indent=4)
