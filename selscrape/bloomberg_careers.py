'''
Created on Sept 10, 2019

Scrap the https://careers.bloomberg.com/job/search careers website for job listings and organize those
  listings into a pandas DataFrame.


@author: bperlman1
'''
import sys,os
import time
from tqdm import tqdm
import re

# These additions to sys.path allow the "from selscrape import sel_scrape as sac"
#  import to work when you are NOT using LiClipse or Eclipse's run system.
if os.path.abspath('.')  not in sys.path:
    if '.' not in sys.path:
        sys.path.append(os.path.abspath('.'))
if os.path.abspath('../')  not in sys.path:
    if '../' not in sys.path and '..' not in sys.path:
        sys.path.append(os.path.abspath('.'))

from selscrape import  sel_scrape as sela
import pandas as pd

# This dictionary contains all of the xpath expressions that one needs to find and extract job data from the jpmorganchase careers site
DICT_XPATH = {
    'job_rows':"//div[@role='listitem']//a",
    "next_page":"//button[contains(@class,'load-more-jobs')]",
    "req":"//p[contains(text(),'Requisition')]",
    "href":"//div[@role='listitem']//a[@class='js-display-job']/@href",
    "title":"//div[contains(@class,'job-name-title')]/h2",
    'location':"//div[contains(@class,'job-name-title')]/h3",
    'full_description':"//div[contains(@class,'job-description-column')]//div[@class='row']//div[@class='col-xs-12']"
}

# jpmorganchase's careers site allow you to chose locations for jobs.
# Below is a list of urls for each location that you want to scrape.
MAIN_URLS =[
    "https://careers.bloomberg.com/job/search?nr=1000&lc=New+York",
    "https://careers.bloomberg.com/job/search?nr=1000&lc=San+Francisco",
    "https://careers.bloomberg.com/job/search?nr=1000&lc=Princeton",
    "https://careers.bloomberg.com/job/search?nr=1000&lc=Washington",
    "https://careers.bloomberg.com/job/search?nr=1000&lc=London",
    "https://careers.bloomberg.com/job/search?nr=1000&lc=Hong+Kong",
    "https://careers.bloomberg.com/job/search?nr=1000&lc=Singapore",
    ]





class Bloomberg(sela.SelDictAccess):
    '''
    Class to scrape job listings from jpmorganchase's careers site, and put those listings into a pandas DataFrame.
    The class inherits from SelDictAccess.
    '''
    def __init__(self,dict_xpath=None,main_urls=None,logger=None):
        super(Bloomberg,self).__init__(DICT_XPATH if dict_xpath is None else dict_xpath,
                                   MAIN_URLS[0] if main_urls is None else main_urls[0],
                                   sac= sela.SelScrape(headless=False),logger=logger)
        if main_urls is None:
            locs = self.get_locations()
            base_url =    "https://careers.bloomberg.com/job/search?nr=1000&lc=CITY"
            url_list = []
            for loc in locs:
                l = loc.replace(' ','+')
                url = base_url.replace('CITY',l)
                url_list.append(url)
            self.main_urls = url_list
        else:
            self.main_urls = main_urls
    
    def get_locations(self):
        location_xpath = "//ul[contains(@aria-labelledby,'c27FilterLabel')]"
        main_url = "https://careers.bloomberg.com/job/search"
        self.sac.goto(main_url)
        t = self.sac.findxpath(location_xpath)['value'][0].get_attribute('innerText')
        locs = re.findall('[A-Za-z][A-Za-z ]+[A-Za-z]', t)
        return locs
    
    def get_jobs(self):
        '''
        This is the main function that iterates through pages of the careers site and extracts jobs data.
        '''
        req = []
        location = []
        descript = []
        job_url = []
        title = []
        for u in self.main_urls:
            self.sac.goto(u)
            self.logger.info(u)
            d = self.find_xpath('job_rows')  
            if  d['status'] is not   None:
                break
            job_rows = d['value']
            hrefs = []
            for job in job_rows:
                h = job.get_attribute('href')
                hrefs.append(h)
            for h in tqdm(hrefs):
                self.sac.goto(h)
                try:
                    this_loc = this_title = this_description = ''
                    this_req = self.find_xpath('req')['value'][0].text
                    if this_req not in req:
                        this_loc  = self.find_xpath('location')['value'][0].text
                        this_title = self.find_xpath('title')['value'][0].text
                        this_description = self.find_xpath('full_description')['value'][0].text
                        # add to arrays
                        job_url.append(h)
                        req.append(this_req)                    
                        location.append(this_loc)
                        descript.append(this_description)
                        title.append(this_title)
                except Exception as e:
                    self.logger.warn(f'Exception on job {h}: {str(e)}')
                    pass
                
                time.sleep(2)
        df = pd.DataFrame({'req':req,'title':title,'location':location,'description':descript,'job_url':job_url})
        return df           
        


if __name__ == '__main__':
    bloomberg = Bloomberg()
    df = bloomberg.get_jobs()
    df.to_csv('./temp_folder/bloomberg_jobs.csv',index=False, encoding = 'utf-8')
    