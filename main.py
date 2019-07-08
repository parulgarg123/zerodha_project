# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 01:10:16 2019

@author: beast
"""

import requests
from bs4 import BeautifulSoup
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import pandas as pd
import redis
import datetime
url = "https://www.bseindia.com/markets/MarketInfo/BhavCopy.aspx"

content = requests.get(url)
print(content.status_code)

soup = BeautifulSoup(content.content, features="lxml")

print('Finding links')
links = list()
for link in soup.find_all('a',  href=True):
    links.append(link['href'])

print('Downloading File')
resp = urlopen(links[0])
zipfile = ZipFile(BytesIO(resp.read()))

df = pd.read_csv(zipfile.open(zipfile.namelist()[0]))
df = df[['SC_CODE', 'SC_NAME', 'OPEN',  'HIGH',  'LOW', 'CLOSE']]
df.columns = ['code', 'name', 'open', 'high', 'low', 'close']
df['name'] = df['name'].str.strip()

df_dict = df.to_dict('records')
date = str(datetime.date.today())
main = {date: df_dict}

r = redis.Redis(host='localhost',  port=6379,  db=0)
print('Saving In DataBase')
inc = 0
for i in df_dict:
    r.hmset(i['code'], i)
    inc += 1

ll = r.keys('*')
#
for i in range(0, len(ll)):
    xx = ll[i].decode()
    ll[i] = int(xx)

ll.sort()
print(ll)

'''
#a = r.hgetall(date+":"+str(ll[0]))
#r.hgetall('name:ABB LTD*')
#ll = r.keys('*')
'''
