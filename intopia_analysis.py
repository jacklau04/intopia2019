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
    
    df_ad_cannabis['type'] = 'x'
    df_ad_oil['type'] = 'y'
    
    df_ad_cannabis['region'] = region
    df_ad_oil['region'] = region
    
    df_final = df_ad_cannabis.append(df_ad_oil)
    return df_final

def convert_production_from_html_to_df(html_file):
    production = pd.read_html(html_file)
    
    df_production = production[1]
    
    name = html_file.split('_')
    product = name[1]
    region = name[2][:2]
    
    df_production = convert_header(df_production)
    
    df_production['type'] = product
    df_production['region'] = region
    
    return df_production

def convert_region(df):
    if df['Area'] == 'Central Canada':
        return 'cc'
    elif df['Area'] == 'Eastern Canada':
        return 'ec'
    elif df['Area'] == 'Western Canada':
        return 'wc'

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

def get_production_data(file_path):
    x_cc_name = path+'/library/'+file_path+'production_x_cc.html'
    x_ec_name = path+'/library/'+file_path+'production_x_ec.html'
    x_wc_name = path+'/library/'+file_path+'production_x_wc.html'
    y_cc_name = path+'/library/'+file_path+'production_y_cc.html'
    y_ec_name = path+'/library/'+file_path+'production_y_ec.html'
    y_wc_name = path+'/library/'+file_path+'production_y_wc.html'
    
    df_x_cc = convert_production_from_html_to_df(x_cc_name)
    df_x_ec = convert_production_from_html_to_df(x_ec_name)
    df_x_wc = convert_production_from_html_to_df(x_wc_name)
    df_y_cc = convert_production_from_html_to_df(y_cc_name)
    df_y_ec = convert_production_from_html_to_df(y_ec_name)
    df_y_wc = convert_production_from_html_to_df(y_wc_name)
    
    df_final = df_x_cc.append(df_x_ec)
    df_final = df_final.append(df_x_wc)
    df_final = df_final.append(df_y_cc)
    df_final = df_final.append(df_y_ec)
    df_final = df_final.append(df_y_wc)
    
    df_final['Unit Production'] = df_final['Unit Production'].astype(int)/1000
    df_final['Company'] = df_final['Company'].astype(int)
    df_final['Grade'] = df_final['Grade'].astype(int)
    
    
    return df_final


def team_tracker(df_team, team_number):
    return df_team[df_team['Team Number'] == team_number]

def production_tracking(df_contact, df_production, item, grade):
    df_contact = df_contact.rename(columns={'Team Number':"Company"})
    df_combine = pd.merge(df_contact, df_production, on='Company', how='outer')
    df_combine = df_combine[df_combine['type'] == item]
    df_combine = df_combine[df_combine['Grade'] == grade]
    
    df_final = df_combine[['Company', 'Grade', 'Unit Production', 'type', 'region']]
    df_final = df_final.drop_duplicates()
    return df_final


