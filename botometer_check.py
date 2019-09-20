#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 17 00:13:41 2019

@author: deepthought42
"""

import botometer

rapidapi_key = "acb37cbbc7msh7915700224ffce9p13a4d3jsn7ae3275cf7dd" # now it's called rapidapi key
twitter_app_auth = {
        'consumer_key' : 'Xa8XbijTP7F3sg0QJ1QUoLq6f',
        'consumer_secret' : 'cRBjxlQK3PO2cy4zFnfZGlLdtIYm1c9KMIe8IsZVaE0OqFIMsh',
        'access_token' : '1092850952284131328-6prMHiiBPsQHU5In4xho9N1cQy9wpO',
        'access_token_secret' : 'BOs3QPs7PnF8uRMgaexuv3BizPPkMeSdXq3YEqATcIsM9'
  }
bom = botometer.Botometer(wait_on_ratelimit=True,
                          rapidapi_key=rapidapi_key,
                          **twitter_app_auth)

# Check a single account by screen name

def user_bom_check(username):
    if isinstance(username,str):
        result = bom.check_account(username)
    elif isinstance(username,list):
        result=bom.check_accounts_in(username)
    return(result)

# Check a single account by id
def user_bom_check_id(user_id):  
    if isinstance(user_id,str):
        result = bom.check_account(user_id)
    elif isinstance(user_id,list):
        result=bom.check_accounts_in(user_id)
    
    
    return(result)



# Check a sequence of accounts
accounts = ['@clayadavis', '@onurvarol', '@jabawack']
#for screen_name, result in bom.check_accounts_in(accounts):
    # Do stuff with `screen_name` and `result`