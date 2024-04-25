#! /usr/bin/env python3
import numpy as np
import pandas as pd
import requests
import re
from bs4 import BeautifulSoup as bf
from datetime import datetime
url = 'https://www.worldometers.info/coronavirus/'
response = requests.get(url)

soup = bf(response.content, 'lxml')
"""with open('Coronavirus_24.html', mode = 'wb')as file:
    file.write(response.content)"""
bloc_countries = soup.find('table',class_="table table-bordered table-hover main_table_countries").contents[3]


#Id in tab 
id_case = bloc_countries.findAll('td', style="font-size:12px;color: grey;text-align:center;vertical-align:middle;")
id_list = [i.contents[0] for i in id_case]

#Country Cases
country_case = bloc_countries.findAll('td', style="font-weight: bold; font-size:15px; text-align:left;")
country_list = [i.contents[0].contents[0] for i in country_case]

#Total_Cases
total_cases_case = bloc_countries.findAll('td', style="font-weight: bold; text-align:right")
total_case_index = [i for i in range(len(total_cases_case)) if i%11 == 0]
list_searched = [total_cases_case[i] for i in total_case_index]
total_cases_list = [i.contents[0] for i in list_searched[:231]]


'''Fuction to convert the website into string 
and filter out contents since it's not possible effectively on some columns'''
#I'm obliged to add manually new cases in dataset , no way to extract directly content
def worldometers_to_string(bloc_countries):
    df_countries = []
    bloc_countries = str(bloc_countries)
    parts = re.findall(r'''(\n<td style="font-size:12px;color: grey;text-align:center;vertical-align:middle;">[\d]*</td>\n[\s\S]*?\n<!-- 1 Case/Death/Test every X -->\n)''',bloc_countries)
    print(len(parts))
    for i in range(len(parts)):
        #Id in tab
        Id_str = re.findall(r'''(grey;text-align:center;vertical-align:middle;">[\d,]+</td>)''',parts[i])
        Id_from_str = re.findall('[\d]+',Id_str[0])[0]
        #Id_from_str

        #Country in tab
        country_str = re.findall(r'''(<a class="mt_a" href="country/[a-zA-Z"/-]+>[a-zA-Z .]+</a>)''',parts[i])
        try:
            country_from_str = re.findall('[a-zA-Z .]+(?#</a>$)',country_str[0])[-2]
        except:
            country_from_str =None
        #country_from_str

        #Total_cases in tab
        total_cases_str = re.findall(r'''(<td style="font-weight: bold; text-align:right">[0-9,]+</td>)''',parts[i])
        try:
            total_cases_from_str = re.findall('[0-9,]+(?#</d>$)',total_cases_str[0])[0]
        except:
            total_cases_from_str = 0
        #total_cases_from_str
    
        #New_cases in tab
        new_cases_str = re.findall(r'''(text-align:right;background-color:#FFEEAA;">[0-9,+]+</td>)''',parts[i])
        try:
            new_cases_from_str = re.findall('[0-9,]+(?#</d>$)',new_cases_str[0])[0]
        except:
            new_cases_from_str = 0
        #new_cases_from_str

        #Total_Deaths in tab
        total_death_str = re.findall(r'''(<td style="font-weight: bold; text-align:right;">[0-9, ]+</td>)''',parts[i])
        try:
            total_death_from_str = re.findall('[0-9,]+(?#</d>$)',total_death_str[0])[0]
        except:
            total_death_from_str =0 
        #total_death_from_str

        #New_deaths in tab
        new_deaths_str = re.findall(r'''(background-color:red; color:white">[0-9,+]+</td>)''',parts[i])
        try:
            new_deaths_from_str = re.findall('[0-9,]+(?#</d>$)',new_deaths_str[0])[-1]
        except:
            new_deaths_from_str = 0
        #new_deaths_from_str

        #Total_Recovered in tab
        total_recovered_str = re.findall(r'''(<span style="color:grey; font-style: italic;">[0-9, ]+</span>)''',parts[i])
        #Affect the extraction of serious_critical cases
        if len(total_recovered_str) == 0:
            try:
                total_recovered_str = re.findall(r'''(<td style="font-weight: bold; text-align:right">[0-9, ]+</td>)''',parts[i])
                total_recovered_from_str = re.findall('[0-9,]+(?#</d>$)',total_recovered_str[1])[0]
            except:
                total_recovered_from_str=0
        else:
            total_recovered_from_str = re.findall('[0-9,]+(?#</d>$)',total_recovered_str[0])[0]
        #total_recovered_from_str

        #New_recovered in tab 
        new_recovered_str = re.findall(r'''(background-color:#c8e6c9; color:#000">[0-9,+]+</td>)''',parts[i])
        try:
            new_recovered_from_str = re.findall('[0-9,]+(?#</d>$)',new_recovered_str[0])[-1]
        except:
            new_recovered_from_str =0
        #new_recovered_from_str

        #Active_cases in tab 
        active_cases_str = re.findall(r'''(<td style="text-align:right;font-weight:bold;">[0-9,]+</td>)''',parts[i])
        try:
            active_cases_from_str = re.findall('[0-9,]+(?#</d>$)',active_cases_str[0])[-1]
        except:
            active_cases_from_str = 0
        #active_cases_from_str

        #Serious_critical, total_cases_per_million, deaths_per_million, tests_per_million in tab (based on this extraction method, depend of total recovered)
        total_recovered_str = re.findall(r'''(<span style="color:grey; font-style: italic;">[0-9, ]+</span>)''',parts[i])
        pattern_search = re.findall(r'''(<td style="font-weight: bold; text-align:right">[0-9,]+</td>)''',parts[i])
        serious_critical_str = re.findall(r'''(<td style="font-weight: bold; text-align:right">[0-9,]+</td>)''',parts[i])
        total_cases_per_million_str = pattern_search
        deaths_per_million_str = pattern_search
        total_tests_str = pattern_search
        tests_per_million_str = pattern_search
        if len(total_recovered_str) == 0:
            total_recovered_str = re.findall(r'''(<td style="font-weight: bold; text-align:right">[0-9, ]+</td>)''',parts[i])
            try:
                serious_critical_from_str = re.findall('[0-9,]+(?#</d>$)',serious_critical_str[2])[0]
            except:
                serious_critical_from_str = 0
            try:
                total_cases_per_million_from_str = re.findall('[0-9,]+(?#</d>$)',total_cases_per_million_str[3])[0]
            except:
                total_cases_per_million_from_str =0
            try:
                deaths_per_million_from_str = re.findall('[0-9,]+(?#</d>$)',total_cases_per_million_str[4])[0]
            except:
                deaths_per_million_from_str = 0
            try:
                total_tests_from_str = re.findall('[0-9,]+(?#</d>$)',total_cases_per_million_str[5])[0]
            except:
                total_tests_from_str = 0
            try:
                tests_per_million_from_str = re.findall('[0-9,]+(?#</d>$)',total_cases_per_million_str[6])[0]
            except:
                tests_per_million_from_str = 0
        else:
            try:
                serious_critical_from_str = re.findall('[0-9,]+(?#</d>$)',serious_critical_str[1])[0]
            except:
                serious_critical_from_str = 0
            try:
                total_cases_per_million_from_str = re.findall('[0-9,]+(?#</d>$)',total_cases_per_million_str[2])[0]
            except:
                total_cases_per_million_from_str =0
            try:
                deaths_per_million_from_str = re.findall('[0-9,]+(?#</d>$)',total_cases_per_million_str[3])[0]
            except:
                deaths_per_million_from_str = 0
            try:
                total_tests_from_str = re.findall('[0-9,]+(?#</d>$)',total_cases_per_million_str[4])[0]
            except:
                total_tests_from_str = 0
            try:
                tests_per_million_from_str = re.findall('[0-9,]+(?#</d>$)',total_cases_per_million_str[5])[0]
            except:
                tests_per_million_from_str = 0
    
            #Population in tab
        population_str = re.findall(r'''(text-align:right"><a href="/world-population/[a-zA-Z"/-]+>[0-9,]+</a>)''',parts[i])
        try :
            population_from_str = re.findall('[0-9,]+(?#</a>$)',population_str[0])[0]
        except:
            population_from_str = None
        #population_from_str

        #Continent in Worldometer tab sheet
        continent_str = re.findall(r'''(<td data-continent[a-zA-Z": =]+>[a-zA-Z. ]+</td>)''',parts[i])
        try:
            continent_from_str = re.findall('[a-zA-Z. ]+(?#</td>$)',continent_str[0])[-2]
        except:
            continent_from_str = None
        #continent_from_str
    

        #DataFrame building 
        df_countries.append({'Id':Id_from_str,
                         'country':country_from_str,
                         'total_cases':total_cases_from_str,
                         'new_cases':new_cases_from_str,
                         'total_death':total_death_from_str,
                         'new_deaths':new_deaths_from_str,
                         'total_recovered':total_recovered_from_str,
                         'new_recovered':new_recovered_from_str,
                         'active_cases':active_cases_from_str,
                         'serious_critical':serious_critical_from_str,
                         'total_cases_per_million':total_cases_per_million_from_str,
                         'deaths_per_million':deaths_per_million_from_str,
                         'total_tests':total_tests_from_str,
                         'tests_per_million':tests_per_million_from_str,
                         'population':population_from_str,
                         'continent':continent_from_str})

    df_coronavirus = pd.DataFrame(df_countries, columns = ['Id','country','total_cases','new_cases','total_death','new_deaths','total_recovered','new_recovered','active_cases','serious_critical','total_cases_per_million','deaths_per_million','total_tests','tests_per_million','population','continent'])
    return df_coronavirus

df = worldometers_to_string(bloc_countries)
tdy = datetime.today().strftime('%Y-%m-%d')
df['datetime'] = tdy

df.to_html('./Coronavirus-'+tdy+'.html',index =False)
