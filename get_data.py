#!/Users/tianranmao/Projects/so1.0/venv/bin/python

# In[1]:


import json
import requests
from bs4 import BeautifulSoup
import datetime
import pytz
import time
import re
import os
import pandas as pd


# In[2]:


def scrape_web(url):
    try:
        source = requests.get(url, timeout=20).text
    except Exception as e:
        print(e)
        return None

    soup = BeautifulSoup(source, 'lxml')

    paragraph = soup.find('p').text

    print(paragraph)
    print()
    return paragraph


# In[3]:


if __name__ == "__main__":
    
    srs = {}
    
    url_510300_mar = "http://yunhq.sse.com.cn:32041//v1/sho/list/tstyle/510300_03?callback=jQuery112402078220234177265_1577088059318&select=contractid%2Clast%2Cchg_rate%2Cpresetpx%2Cexepx&order=contractid%2Cexepx%2Case&_=1577088059356"

    url_510300_apr = "http://yunhq.sse.com.cn:32041//v1/sho/list/tstyle/510300_04?callback=jQuery112409417454011549969_1582766597079&select=contractid%2Clast%2Cchg_rate%2Cpresetpx%2Cexepx&order=contractid%2Cexepx%2Case&_=1582766597086"

    url_510300_jun = "http://yunhq.sse.com.cn:32041//v1/sho/list/tstyle/510300_06?callback=jQuery112402078220234177265_1577088059336&select=contractid%2Clast%2Cchg_rate%2Cpresetpx%2Cexepx&order=contractid%2Cexepx%2Case&_=1577088059360"

    url_510300_sep = "http://yunhq.sse.com.cn:32041//v1/sho/list/tstyle/510300_09?callback=jQuery11240028350739831281335_1579742947846&select=contractid%2Clast%2Cchg_rate%2Cpresetpx%2Cexepx&order=contractid%2Cexepx%2Case&_=1579742947854"

    url_510300 = "http://yunhq.sse.com.cn:32041//v1/sh1/line/510300?callback=jQuery1124083017185515941_1577089469213&begin=0&end=-1&select=time%2Cprice%2Cvolume&_=1577089469215"
    
    url_510050_mar = "http://yunhq.sse.com.cn:32041/v1/sho/list/tstyle/510050_03?callback=jQuery111206287606767948288_1564018683263&select=contractid%2Clast%2Cchg_rate%2Cpresetpx%2Cexepx&_=1564018683268"

    url_510050_apr = "http://yunhq.sse.com.cn:32041//v1/sho/list/tstyle/510050_04?callback=jQuery112409417454011549969_1582766597079&select=contractid%2Clast%2Cchg_rate%2Cpresetpx%2Cexepx&order=contractid%2Cexepx%2Case&_=1582766597082"

    url_510050_jun = "http://yunhq.sse.com.cn:32041/v1/sho/list/tstyle/510050_06?callback=jQuery111209494863322515489_1571879875297&select=contractid%2Clast%2Cchg_rate%2Cpresetpx%2Cexepx&_=1571879875304"

    url_510050_sep = "http://yunhq.sse.com.cn:32041//v1/sho/list/tstyle/510050_09?callback=jQuery11240028350739831281335_1579742947844&select=contractid%2Clast%2Cchg_rate%2Cpresetpx%2Cexepx&order=contractid%2Cexepx%2Case&_=1579742947849"

    url_510050 = "http://yunhq.sse.com.cn:32041/v1/sh1/line/510050?callback=jQuery111208396578891098054_1563195335181&begin=0&end=-1&select=time%2Cprice%2Cvolume & _ =1563195335188"
    
    url_list = [url_510300, url_510300_mar, url_510300_apr, url_510300_jun, url_510300_sep, url_510050, url_510050_mar, url_510050_apr, url_510050_jun, url_510050_sep]

    while True:
        now_shanghai = datetime.datetime.now(tz=pytz.timezone('Asia/Shanghai'))
        file_txt = f"./txt/{now_shanghai.strftime('%Y-%m-%d')}.txt"
        file_csv = f"./csv/{now_shanghai.strftime('%Y-%m-%d')}.csv"

        if not os.path.exists(file_txt):
            with open(file_txt, 'w') as f:
                pass
            
        if not os.path.exists(file_csv):
            with open(file_csv, 'w') as f:
                pass
            
        for url in url_list:
            paragraph = scrape_web(url)

            if paragraph!=None:

                pattern_json = re.compile('jQuery[\d_]+\((.*)\)')  
                match_json = re.search(pattern_json, paragraph)
                data = json.loads(match_json.group(1))
                
                
                webdate = data['date']

                webtime = data['time']


                time_start = 93000
                time_break = 113000
                time_restart = 130000
                time_stop = 150000
                time_near = 91500

                market_open = (webtime >=  time_start and webtime <=  time_break) or (webtime >=  time_restart and webtime <=  time_stop)
                nearly_open = (time_break < webtime and webtime <  time_restart) or (time_near < webtime < time_start)

                if market_open:
                    with open(file_txt, 'a') as f:
                        try:
                            f.write(paragraph)
                            f.write('\n')
                            print('writing to file...')
                        except Exception as e:
                            print(e)
                            
                    datetime_obj = datetime.datetime.strptime(str(webdate)+str(webtime).rjust(6,'0'), '%Y%m%d%H%M%S')

                    if 'code' in data:
                        if data['code'] not in srs:
                            s = pd.Series(name=data['code'], index=[datetime_obj], data=[data['line'][-1][-2]])
                            s = s.resample('T').mean()
                            srs.update({data['code']: s})
                        else:
                            srs[data['code']] = srs[data['code']].append(pd.Series(name=data['code'], index=[datetime_obj], data=[data['line'][-1][-2]]))
                            srs[data['code']] = srs[data['code']].resample('T').mean()

                    else:
                        for op in data['list']:
                            if op[0].split()[0] not in srs:
                                s = pd.Series(name=op[0].split()[0], index=[datetime_obj], data=[op[1]])
                                s = s.resample('T').mean()
                                srs.update({op[0].split()[0]: s})
                            else:
                                srs[op[0].split()[0]] = srs[op[0].split()[0]].append(pd.Series(name=op[0].split()[0], index=[datetime_obj], data=[op[1]]))
                                srs[op[0].split()[0]] = srs[op[0].split()[0]].resample('T').mean()
                                
        
        if market_open:
            df_w = pd.concat(srs.values(), axis=1)
            df_w.index.name = 'time'
            df_w.to_csv(file_csv)
        
        webtime = str(webtime).rjust(6, '0')
        
        if market_open:
            print(f'{webtime[0:2]:>2}:{webtime[2:4]}:{webtime[4:]} markets open')                                                                     

        elif nearly_open:
            print(f'{webtime[0:2]:>2}:{webtime[2:4]}:{webtime[4:]} markets opening soon') 
            print('waiting for 10 seconds')
            time.sleep(10)
        else:
            print(f'{webtime[0:2]:>2}:{webtime[2:4]}:{webtime[4:]} markets closed') 
            print('waiting for 10 minutes')
            time.sleep(600)                


# In[9]:


# df = pd.read_csv(file_csv, index_col='time', parse_dates=['time'])


# In[ ]:




