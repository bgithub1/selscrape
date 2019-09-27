'''
Created on Jan 2, 2018

Scrap the jpmorganchase careers website for job listings and organize those
  listings into a pandas DataFrame.


@author: bperlman1
'''
import sys,os
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
    'job_rows':"//tr[@role='row']/td[@class='coloriginaljobtitle']/a",
    "next_page":"//a[@class='pager-next']",
    "req":"//div[@class='req']",
    'city':"//strong[contains(text(), 'Location:')]/following::span",
    'state':"//strong[contains(text(), 'Location:')]/following::span/following::span",
    'country': "//strong[contains(text(), 'Location:')]/following::span/following::span/following::span",
    'full_description':"//div[@class='jobdescriptiontbl']"
}

# jpmorganchase's careers site allow you to chose locations for jobs.
# Below is a list of urls for each location that you want to scrape.
MAIN_URLS =[
    "https://jobs.chase.com/ListJobs/All/Country-US/State-NY/City-New-York/",
    "https://jobs.chase.com/ListJobs/All/Country-US/State-NJ/City-Jersey-City/"
    ]





class Chase(sela.SelDictAccess):
    '''
    Class to scrape job listings from jpmorganchase's careers site, and put those listings into a pandas DataFrame.
    The class inherits from SelDictAccess.
    '''
    def __init__(self,dict_xpath=None,main_urls=None):
        super(Chase,self).__init__(DICT_XPATH if dict_xpath is None else dict_xpath,
                                   MAIN_URLS[0] if main_urls is None else main_urls[0],
                                   sac= sela.SelScrape(headless=False))
        self.main_urls = MAIN_URLS if main_urls is None else main_urls
        
    
    def get_jobs(self):
        '''
        This is the main function that iterates through pages of the careers site and extracts jobs data.
        '''
        req = []
        city = []
        state = []
        country = []
        descript = []
        job_url = []
        for u in self.main_urls:
            self.sac.goto(u)
            page_num = 0
            last_url = u
            for _ in range(1000):
                d = self.find_xpath('job_rows')  
                if  d['status'] is not   None:
                    break
                job_rows = d['value']
                hrefs = []
                for job in job_rows:
                    h = job.get_attribute('href')
                    hrefs.append(h)
                for h in hrefs:
                    self.sac.goto(h)
#                     req.append(self.find_xpath('req')['value'][0].text)                    
                    this_req = self.find_xpath('req')['value'][0].text
                    if this_req not in req:
                        job_url.append(h)
                        req.append(this_req)                    
                        city.append(self.find_xpath('city')['value'][0].text)
                        state.append(self.find_xpath('state')['value'][0].text)
                        country.append(self.find_xpath('country')['value'][0].text)
                        descript.append(self.find_xpath('full_description')['value'][0].text)
#                 print("processed page %d" %(page_num))
                print(f"processed page: {page_num}  num jobs: {len(req)}")
                self.sac.goto(last_url)
                np = self.find_xpath('next_page')
                if np['status'] is None:
                    page_num += 1
                    self.click_element('next_page')
                    last_url = self.sac.driver.current_url
                else:
                    print('f''total for %s: %d' %(u,len(req)))
                    break
        df = pd.DataFrame({'req':req,'city':city,'state':state,'country':country,'description':descript,'job_url':job_url})
        df['title'] = df.description.apply(lambda v: v.split('Req')[0].replace('\n','')) 
        return df           
        


if __name__ == '__main__':
    chase = Chase()
    df = chase.get_jobs()
    df.to_csv('./temp_folder/chase_jobs.csv',index=False, encoding = 'utf-8')
    