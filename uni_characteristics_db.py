
#==========================================================================================
# SETTING THE PACKAGES TO USE

# Standard packages
import os
import pandas as pd
import numpy as np
from geopy.geocoders import Nominatim
from SPARQLWrapper import SPARQLWrapper, JSON, N3
from tqdm import tqdm

# For web scrapping
import requests
import bs4
from bs4 import BeautifulSoup, NavigableString
from lxml.html.soupparser import fromstring
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time


#==========================================================================================
# Path

path='/Users/balcazar/Dropbox/JOB MARKET APPLICATIONS/'
#path='/Users/cfb310/Dropbox/JOB MARKET APPLICATIONS/'

# Load previously collected jobs
try:
    job_prev = pd.read_csv(path+'job_market_db_2023.csv')['jobid'].unique()
except:
    None

#==========================================================================================
# CONSTRUCTING THE CHARACTERISTICS DATABASE 
#==========================================================================================
# Driver path
cdpath='/Users/balcazar/Dropbox/geckodriver'
#cdpath='/Users/balcazar/Dropbox/chromedriver_office'

job_df = pd.read_csv(path+'apsa_jb_db.csv',sep=',')
job_db = job_df.drop_duplicates(subset=['jobid'])
job_db = job_df.fillna('')
job_db = job_df.drop_duplicates(subset=['company'])
company_aux = list(job_db['company'])

# Loading DBPedia
driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
time.sleep(5)
driver.get('https://lookup.dbpedia.org/index.html')
sparql = SPARQLWrapper('https://dbpedia.org/sparql')
passw=driver.find_element(By.ID,'query')

rank_us = []; rank_wus = []; rank_qs = []; rank_la = []; rank_rg = [];

# Scrapping wikipedia with API
for school in tqdm(company_aux):
    try:
        # Navigation
        passw.send_keys(school)
        time.sleep(5)
        driver.find_element(By.ID,'search-button').click()
        time.sleep(5)
        passw.clear()
            
        search=driver.find_element(By.XPATH,'//*[(@id = "result-panel")]')
            
        # Obtain query 
        tree = fromstring(driver.page_source)
        db_responder=tree.xpath("//*[(@id = 'response-panel')]//div[(((count(preceding-sibling::*) + 1) = 1) and parent::*)]//a / text()")
        db_responder=str(db_responder).replace('http://dbpedia.org/resource/','').replace("['","").replace("']","")
        
    
        # Extract data - if one value if missing in the entery query, then the entire JSON will be empty
        try: 
            sparql.setQuery(f'''
                                SELECT ?rank_us
                                WHERE {{ dbr:{db_responder} dbp:usnwrNu ?rank_us.
                                        }}''')
            sparql.setReturnFormat(JSON)
            query_response = sparql.query().convert()
            rank_us.append([query_response['results']['bindings'][0]['rank_us']['value'],school])
        except:
            rank_us.append('')
                
        try: 
            sparql.setQuery(f'''
                                SELECT ?rank_wus
                                WHERE {{ dbr:{db_responder} dbp:usnwrW ?rank_wus.
                                        
                                        }}''')
            sparql.setReturnFormat(JSON)
            query_response = sparql.query().convert()
            rank_wus.append([query_response['results']['bindings'][0]['rank_wus']['value'],school])
        except:
            rank_wus.append('')
            
        try:
            sparql.setQuery(f'''
                                SELECT ?rank_qs
                                WHERE {{ dbr:{db_responder} dbp:qsW ?rank_qs.
                                        
                                        }}''')
            sparql.setReturnFormat(JSON)
            query_response = sparql.query().convert()
            rank_qs.append([query_response['results']['bindings'][0]['rank_qs']['value'],school])
        except:
            rank_qs.append('')
        
        try:
            sparql.setQuery(f'''
                                SELECT ?rank_la 
                                WHERE {{ dbr:{db_responder} dbp:usnwrLa ?rank_la.
                                        
                                        }}''')
            sparql.setReturnFormat(JSON)
            query_response = sparql.query().convert()
            rank_la.append([query_response['results']['bindings'][0]['rank_la']['value'],school])
        except:
            rank_la.append('')
        
        try:
            sparql.setQuery(f'''
                                SELECT  ?rank_rg
                                WHERE {{ dbr:{db_responder} dbp:usnwrReg ?rank_rg.
                                        
                                        }}''')
            sparql.setReturnFormat(JSON)
            query_response = sparql.query().convert()
            rank_rg.append([query_response['results']['bindings'][0]['rank_rg']['value'],school])
        except:
            rank_rg.append('')
        
        time.sleep(10)
        
    except:
        print("Error with " + str(school))
        
        time.sleep(10)

driver.close()

chr_df = pd.DataFrame({'company_aux': company_aux,  
                        'rank_us': rank_us,
                        'rank_wus': rank_wus,
                        'rank_qs': rank_qs, 
                        'rank_la': rank_la, 
                        'rank_rg': rank_rg,})

chr_df.to_csv(path+'charac_db.csv',sep=',')
#==========================================================================================
# Obtain geographical coordinates
job_df = pd.read_csv(path+'apsa_jb_db.csv',sep=',')
job_db = job_df.drop_duplicates(subset=['jobid'])
job_db = job_df.fillna('')
job_db = job_df.drop_duplicates(subset=['company'])
company_aux = list(job_db['company'])

geolocator = Nominatim(user_agent="gmaps")
lat = []; lon = []; city = []; county = []; state = []; country = [];
for school in tqdm(company_aux):
    try:
        location = geolocator.geocode(str(school), addressdetails=True).raw        
        lat.append([location['lat'],school])
        lon.append([location['lon'],school])

        try: 
            country.append([location['address']['country_code'],school])
        except:
            country.append('')
        
        try: 
            city.append([location['address']['city'],school])
        except:
            city.append('')
            
        try:
            county.append([location['address']['county'],school])
        except:
            county.append('')
            
        try:
            state.append([location['address']['state'],school])
        except:
            state.append('')

        time.sleep(10)    
        # To do: build amenities' score
        
    except:
        lat.append(''); lon.append(''); city.append(''); county.append(''); state.append(''); country.append('');
        print("Error with " + str(school))
        time.sleep(10)

loc_df = pd.DataFrame({'company_aux': company_aux,
                       'lat': lat, 
                       'lon': lon, 
                       'city': city, 
                       'county': county , 
                       'state': state, 
                       'country': country})

loc_df.to_csv(path+'locatiom_db.csv',sep=',')