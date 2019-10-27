#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandas as pd
import os
import glob

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
    
def convert_valueadded_from_html_to_df(html_file):
    value_added = pd.read_html(html_file)
    period = html_file[-12:-5]
    df_value_added = value_added[0]
    df_value_added = convert_header(df_value_added)
    value_added = df_value_added['Value Added']
    value_added = pd.DataFrame(value_added)
    value_added = (value_added['Value Added'].replace( '[\$,)]','', regex=True )
                   .replace( '[(]','-',   regex=True ).astype(float))
    column_name = "value_"+period
    df_value_added[column_name] = value_added

    return df_value_added
    
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

def get_value_added_data(file_dir):

    file_path = path + "/library/" + file_dir + "*.html"
    file_list = glob.glob(file_path)

    new_list = []

    for file in file_list:
        actual_file = file.replace('\\','/')
        new_list.append(actual_file)

    for n in range(len(new_list)):
        if n == 0:
            df_final = convert_valueadded_from_html_to_df(new_list[n])
            df_final = df_final[['Company', 'Strategy' ,'value_period2']]
        else:
            df_new = convert_valueadded_from_html_to_df(new_list[n])
            period = new_list[n][-12:-5]
            column_name = "value_"+period
            df_new = df_new[['Company', column_name]]
            df_final = pd.merge(df_final, df_new, how='outer' , on='Company')
            
    df_final['Company'] = df_final['Company'].astype(int)
    df_final = df_final.sort_values(by='Company', ascending=True)
    return df_final

def analysis_value_added_data(df_value, starting, ending):
    number_of_row = df_value.shape[1] - 3
    for n in range(number_of_row):
        num = ending - starting + 1
        if n == 0:
            column = "difference_" + str(starting)
            starting_column = 'value_period' + str(starting)
            df_value[column] = df_value[starting_column] - 0
            
        elif n > 0 and n < num:
            column = "difference_" + str(starting + n)
            starting_column = 'value_period' + str(starting+n-1)
            second_column = 'value_period' + str(starting+n)
            df_value[column] =  df_value[second_column] - df_value[starting_column]
        else:
            break
    
    return df_value

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


