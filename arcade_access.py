#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 21 13:46:56 2021

@author: deepthought42

#code to extract data form the arcade api
"""

import requests
from requests.structures import CaseInsensitiveDict
api_token='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoiNzdmYWM2NDQtZGQyMy00YTM2LWFhOGEtNWNmNzIzNTk4YTgxIiwiYXVkIjoiZmFzdGFwaS11c2VyczphdXRoIiwiZXhwIjoxNjMyMjI3NzI5fQ.-q2tbYWvw6C16AL3jUEFPGEO4CiWch8BL5-TK7SS41E'

username="a.mikaelian@thinktankmaths.com"
password="a1r9a4m2!"

new_token=0
try:
    print(toke)
except NameError:
    toke=""

cat_id=42842
cat_id=13764

if new_token or len(toke)==0:
    
    url='https://arcade.spacetech-ibm.com/auth/register'
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    
    data='{ "email": "'+username+'", "password": "'+password+'" }'
    
    response=requests.post(url,data=data,headers=headers)
    
    print('response to register curl '+response.text)
    
    
    url='https://arcade.spacetech-ibm.com/auth/jwt/login'
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    #data="'username="+username+"&password="+password+"'"
    data="username=a.mikaelian@thinktankmaths.com&password=a1r9a4m2!"
    response2=requests.post(url,data=data,headers=headers)
    
    toke=response2.json()['access_token']
    
    print(response2.text)



#ephemeris

url = "https://arcade.spacetech-ibm.com/ephemeris/"+str(cat_id).zfill(5)

headers = CaseInsensitiveDict()
headers["accept"] = "application/json"
headers["Authorization"] = "Bearer "+toke
headers["stop_time"]="2021-09-20T12:00:00.000"

data_return = requests.get(url, headers=headers,data=data)

data_json=data_return.json

data_dict=data_json()[0]


url = 'https://arcade.spacetech-ibm.com/asos'

headers = CaseInsensitiveDict()
headers["accept"] = "application/json"
headers["Authorization"] = "Bearer "+toke
headers["stop_time"]="2021-09-20T12:00:00.000"

data_return1 = requests.get(url, headers=headers,data=data).json

data_dict1=data_return1()

ids_list=[]
for entry in data_dict1:
    ids_list.append(int(entry['norad_id']))
ids_list.sort()



url = 'https://arcade.spacetech-ibm.com/interpolate/'+str(cat_id).zfill(5)

headers = CaseInsensitiveDict()
headers["accept"] = "application/json"
headers["Authorization"] = "Bearer "+toke

data_return2 = requests.get(url, headers=headers,data=data).json

data_dict2=data_return2()[0]









