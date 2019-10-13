#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import os
path = r'%s' % os.getcwd().replace('\\','/')

def convert_header(df):
    headers = df.iloc[0]
    new_df = pd.DataFrame(df.values[1:], columns=headers)
    return new_df

def convert_ad_from_html_to_df(html_file):
    ad = pd.read_html(html_file)
    name = html_file.split('_')
    region = name[1][:2]
    
    ad_cannabis = ad[0]
    ad_oil = ad[1]
    
    df_ad_cannabis = convert_header(ad_cannabis)
    df_ad_oil = convert_header(ad_oil)
    
    df_ad_cannabis['type'] = 'cannabis'
    df_ad_oil['type'] = 'oil'
    
    df_ad_cannabis['region'] = region
    df_ad_oil['region'] = region
    
    df_final = df_ad_cannabis.append(df_ad_oil)
    return df_final

def convert_region(df):
    if df['Area'] == 'Central Canada':
        return 'cc'
    elif df['Area'] == 'Eastern Canada':
        return 'ec'
    elif df['Area'] == 'Western Canada':
        return 'wc'

def team_tracker(df,team_number):
    return df[df['Team Number'] == team_number]
    
def get_advertising_data(file_path):
    ec_name = path+'/library/'+file_path+'advertising_ec.html'
    wc_name = path+'/library/'+file_path+'advertising_wc.html'
    cc_name = path+'/library/'+file_path+'advertising_cc.html'
    
    df_ec = convert_ad_from_html_to_df(ec_name)
    df_wc = convert_ad_from_html_to_df(wc_name)
    df_cc = convert_ad_from_html_to_df(cc_name)
    
    df_final = df_ec.append(df_wc)
    df_final = df_final.append(df_cc)
    df_final['Total'] = df_final['Total'].astype(float)
    df_final = df_final[df_final['Total'] > 0]
    
    return df_final

def get_live_price_data(file_path):
    df = pd.read_html(path+'/library/'+file_path+'/consumer_price_live.html')[0]
    df = convert_header(df)
    df['region'] = df.apply(convert_region, axis=1)
    return df

