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
# SCRAPING THE VARIABLES DESCRIPTIONS 
#==========================================================================================
# Driver path
cdpath='/Users/balcazar/Dropbox/geckodriver'
#cdpath='/Users/balcazar/Dropbox/chromedriver_office'

driver = webdriver.Firefox(executable_path=GeckoDriverManager().install())
time.sleep(5)

website='https://www.apsanet.org/Sign-In?ReturnURL=/CAREERS/eJobs/eJobs-Online/JBctl'

#==========================================================================================
# Execute driver on page an log-in
#==========================================================================================
driver.get(website)

# Login
login=driver.find_element(By.ID,'dnn_ctr3337_View_ctl00_tbUserName')
login.send_keys('****') # Reaplce with own login name
time.sleep(5)

# Password
passw=driver.find_element(By.ID,'dnn_ctr3337_View_ctl00_tbPassword')
passw.send_keys('*****') # Replace with own password
time.sleep(5)

# Navigation to job list
driver.find_element(By.ID,'dnn_ctr3337_View_ctl00_btnSignIn').click()
time.sleep(5)

driver.find_element(By.ID,'dnn_ctr4356_ViewJobBank_Candidate_lb_JobSearch').click()
time.sleep(5)


#==========================================================================================
# Obtain data on jobs
#==========================================================================================

# Data set columns
jobid = [ ]; dateavailable = [ ]; deadline = [ ]; title = [ ]; department = [ ]; company = [ ];
urank=[]; utype=[]; position = [ ]; subfield1 = [ ]; subfield2 = [ ]; subfield3 = [ ];	
expertise1 = [ ]; expertise2 = [ ];	 expertise3 = [ ];
region = [ ]; salaryrange = [ ]; searchstatus = [ ]; jobtext = [ ]; description = [];

# Looping through pages
pbar = tqdm(total=10*25) # Pages times jobs per page

for i in range(1,10):
    try:
        # Navigation to different job list pages
        element = driver.find_element(By.XPATH,"//table[@id='dnn_ctr4356_ViewJobBank_JobSearch_rg_MyJobs_ctl00']"+ \
                                  "/tfoot/tr/td/table/tbody/tr/td/div[2]/a["+str(i)+"]/span")
        driver.execute_script("arguments[0].click();",element)
        time.sleep(5)
        
        # Obtain links to all jobs in page
        soup = BeautifulSoup(driver.page_source, "html.parser")
        links = [a['href'] for a in soup.select('span a',href=True) if a.text]
        links = [item for item in links if 'JobID' in item]
        links = [*set(links)]
        
        # Deleting links collected
        try: 
            links = [ link for link in links 
                    if int(str(link).replace('https://www.apsanet.org/CAREERS/eJobs/eJobs-Online/JBctl/ViewJob/JobID/',''))
                    not in list(job_prev)] 
        except:
            None

        
        for link in links:
            
            try:
                
                # Obtain metadata from link
                page = requests.get(link)
                driver.implicitly_wait(5)
                driver.get(link)
                soup_job = BeautifulSoup(driver.page_source, 'html.parser') 
                
                # Store job information
                jobid.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lbl_JobID').text)
                dateavailable.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_DateAvailable').text)
                deadline.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Deadline').text)
                title.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Title').text)
                department.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Department').text)
                company.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Company').text)
                position.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Position').text)
                subfield1.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Subfield1').text)
                subfield2.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Subfield2').text)
                subfield3.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Subfield3').text)
                expertise1.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Expertise1').text)
                expertise2.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Expertise2').text)
                expertise3.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Expertise3').text)
                region.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_Region').text)
                salaryrange.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_SalaryRange').text)
                searchstatus.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_SearchStatus').text)
                
                # Description
                for br in soup_job.find_all("br"):
                    br.replace_with("\n")
                description.append(soup_job.select_one('fieldset #dnn_ctr4356_ViewJobBank_ViewJob_lb_JobText span').text)
            
                time.sleep(5)
                
                driver.get('https://www.apsanet.org/CAREERS/eJobs/eJobs-Online/JBctl/JobSearch')

                pbar.update(1)
            except:
                print("Error with JobID " + str(link))
                
                time.sleep(5)
                
                driver.get('https://www.apsanet.org/CAREERS/eJobs/eJobs-Online/JBctl/JobSearch')
    
    except:
        print("Error with job page " + str(i))
        time.sleep(5)
        
        driver.get('https://www.apsanet.org/CAREERS/eJobs/eJobs-Online/JBctl/JobSearch')


pbar.close()
driver.close()

#==========================================================================================
 # Create data base on jobs

job_df = pd.DataFrame({'jobid': jobid,  
                        'dateavailable': dateavailable,
                        'deadline': deadline,
                        'title': title,
                        'department': department,
                        'company': company,
                        'position': position,
                        'subfield1': subfield1,
                        'subfield2': subfield2,
                        'subfield3': subfield3,
                        'expertise1': expertise1,
                        'expertise2': expertise2,
                        'expertise3': expertise3,
                        'region': region,
                        'salaryrange': salaryrange,
                        'searchstatus': searchstatus,
                        'description': description })

job_df.to_csv(path+'apsa_jb_db.csv',sep=',')

#==========================================================================================
# Mergining and saving
#===========================================================================================
job_df = pd.read_csv(path+'apsa_jb_db.csv',sep=',')
chr_df = pd.read_csv(path+'charac_db.csv',sep=',')
loc_df = pd.read_csv(path+'locatiom_db.csv',sep=',')
# Cleaning
for i in range(0,7):
    for j in range(0,len(chr_df.iloc[:,i])):
        try:
            chr_df.iloc[:,i][j]=chr_df.iloc[:,i][j].split("'")[1]
        except:
            None
for i in range(0,8):
    for j in range(0,len(loc_df.iloc[:,i])):
        try:
            loc_df.iloc[:,i][j]=loc_df.iloc[:,i][j].split("'")[1]
        except:
            None                      
                    
    
# Create empty columns in jb_extra
jb_extra=job_df.merge(loc_df, left_on='company', right_on='company_aux', how='outer') 
jb_extra=jb_extra.merge(chr_df, left_on='company', right_on='company_aux', how='outer')


# Appending
'''
try:
    jb_extra.append(pd.read_csv(path+'job_market_db_2023.csv'), ignore_index=True)  
except:
    None 
'''
# Saving
jb_extra = jb_extra.drop_duplicates(subset=['jobid'])
jb_extra = jb_extra.fillna('')
jb_extra.to_csv(path+'job_market_db_2023.csv',sep=',')
    




