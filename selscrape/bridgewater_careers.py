'''
Created on Sep 12, 2019

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
import datetime
import re
import pathlib
import traceback

def scroll_shim(passed_in_driver, object):
    '''
    Execute a scroll operation to avoid an element being off the page
      when you try to click it
    :param passed_in_driver:
    :param object:
    '''
    x = object.location['x']
    y = object.location['y']
    scroll_by_coord = 'window.scrollTo(%s,%s);' % (
        x,
        y
    )
    scroll_nav_out_of_way = 'window.scrollBy(0, -120);'
    passed_in_driver.execute_script(scroll_by_coord)
    passed_in_driver.execute_script(scroll_nav_out_of_way)

DICT_XPATH = {
    'title':"//div[@class='opening']//a",
    'href':"//div[@class='opening']//a",
    'locs':"//div[@class='opening']//span[@class='location']",
    'full_description':"//div[@id='content']",
}
MAIN_URL ="https://boards.greenhouse.io/bridgewater89"
HOME_FOLDER = str(pathlib.Path.home())


class Bridgewater(sela.SelDictAccess):
    '''
    Class to scrape job listings from Blackrock's careers site, and put those listings into a pandas DataFrame.
    The class inherits from SelDictAccess.
    '''
    def __init__(self,dict_xpath=None,main_urls=None,logger=None):
        super(Bridgewater,self).__init__(DICT_XPATH if dict_xpath is None else dict_xpath,
                                   MAIN_URL if main_urls is None else main_urls[0],
                                   sac= sela.SelScrape(headless=False),logger=logger)



    def click_read_more(self,ind,df):
        driver = self.sac.driver
        self.sac.goto(df.loc[ind].job_url)
        source_element = self.find_xpath('read_more')['value'][0]
        if 'firefox' in driver.capabilities['browserName']:
            scroll_shim(driver, source_element)
        actions = sela.webdriver.ActionChains(driver)
        actions.move_to_element(source_element)
        actions.click()
        actions.perform()

    def get_job_details(self,df,index_start=0):
        '''
        Click on each url in df, and extract job description in full
          and the job requisition number
        :param df:
        :param index_start:
        '''
        descriptions = []
        reqs = []
        inds = []
        
        for ind in tqdm([k for k in df.index if k>=index_start]): 
            req = 0
            description = None
            try:
                self.sac.goto(df.loc[ind].job_url)
                time.sleep(.5)
                description_element_list = self.find_xpath('full_description')['value']
                description = description_element_list[0].text
            except Exception as e2:
                traceback.print_exc()    
            self.logger.info(f'finished index {ind}. req = {req}')
                        
            descriptions.append(description)
            inds.append(ind)
        df_req_desc = pd.DataFrame({'description':descriptions},index=inds)
        df_new = df.join(df_req_desc)
        return df_new
        
    def get_jobs(self):
        '''
        Create a DataFrame that contains urls to bridgewater jobs
        '''
        df = None
        self.sac.goto(MAIN_URL)
        try:
            d = {
                'title':[e.text for e in self.find_xpath('title')['value']],
                'job_url':[e.get_attribute('href') for e in self.find_xpath('href')['value']],
                'location':[e.text for e in self.find_xpath('locs')['value']],
            }
            df_temp = pd.DataFrame(d)
            if df is None:
                df = df_temp.copy()
            else:
                df = df.append(df_temp,ignore_index=True)
                df.index = list(range(len(df)))
        except Exception as e:
            traceback.print_exc()
        df['job_num'] = df.job_url.apply(lambda s:re.findall('jobs\/[0-9]{5,12}',s)[0].replace('/','').replace('jobs',''))
        return df
        
if __name__ == '__main__':
    bridgewater = Bridgewater()
    df = bridgewater.get_jobs()
    df.to_csv('./temp_folder/bridgewater_links.csv',index=False, encoding = 'utf-8')
    df2 = bridgewater.get_job_details(df)
    df2.to_csv('./temp_folder/bridgewater_jobs.csv',index=False, encoding = 'utf-8')
