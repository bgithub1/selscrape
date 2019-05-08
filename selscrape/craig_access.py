'''
Created on May 06, 2019

Access listing from any set of geo locations in Craigslist.

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
        sys.path.append(os.path.abspath('../'))
        
from selscrape import sel_scrape as sac
import traceback
import pandas as pd
import datetime
import re

DICT_CRAIG_ACCESS_ATTRIBUTES_XPATH = {
    'price':"//span[@class='postingtitletext']/span[@class='price']",
    'page_title':"//span[@class='postingtitletext']/span[@id='titletextonly']",
    'auto_condition':'//section[@class="userbody"]/div[@class="mapAndAttrs"]/p[@class="attrgroup"]/span[contains(text(),"condition")]/b',
    'cylinders':'//section[@class="userbody"]/div[@class="mapAndAttrs"]/p[@class="attrgroup"]/span[contains(text(),"cylinders")]/b',
    'drive':'//section[@class="userbody"]/div[@class="mapAndAttrs"]/p[@class="attrgroup"]/span[contains(text(),"drive")]/b',
    'fuel':'//section[@class="userbody"]/div[@class="mapAndAttrs"]/p[@class="attrgroup"]/span[contains(text(),"fuel")]/b',
    'odometer':'//section[@class="userbody"]/div[@class="mapAndAttrs"]/p[@class="attrgroup"]/span[contains(text(),"odometer")]/b',
    'paint_color':'//section[@class="userbody"]/div[@class="mapAndAttrs"]/p[@class="attrgroup"]/span[contains(text(),"paint color")]/b',
    'title_status':'//section[@class="userbody"]/div[@class="mapAndAttrs"]/p[@class="attrgroup"]/span[contains(text(),"title status")]/b',
    'transmission':'//section[@class="userbody"]/div[@class="mapAndAttrs"]/p[@class="attrgroup"]/span[contains(text(),"transmission")]/b',
}


class CraigAccess(sac.SelScrape):
    def __init__(self,
        headless=None,
        geos_csv_path=None,
        geo_locations_url=None,
        beg_geo_index=None,
        end_geo_index=None,
        output_folder_path=None,
        make=None,
        model=None,
        max_auto_year=None,
        min_auto_miles=0,
        max_auto_miles=500000,
        auto_transmission=1,
        titles_only=False,
        has_image=False,
        posted_today=False,
        logger=None):
        
        super(CraigAccess,self).__init__(headless)
        self.logger = logger if logger is not None else sac.init_root_logger('logfile.log', 'INFO')
        if geos_csv_path is None:
            self.df_geos = self._get_geos(geo_locations_url)
            self.df_geos.to_csv(geos_csv_path,index=False)
        else:
            self.df_geos  = pd.read_csv(geos_csv_path)
        self.beg_geo_index = 0 if beg_geo_index is None else beg_geo_index 
        self.end_geo_index = len(self.df_geos)-1 if end_geo_index is None else end_geo_index 
        self.output_folder_path = './temp_folder' if output_folder_path is None else output_folder_path
        self.make = 'BMW' if make is None else make
        self.model = '635' if model is None else model
        self.max_auto_year = datetime.datetime.now().year if max_auto_year is None else max_auto_year
        self.min_auto_miles = min_auto_miles
        self.max_auto_miles = max_auto_miles
        self.auto_transmission = f'auto_transmission_{auto_transmission}'
        self.titles_only = '' if titles_only is False else '&srchType=T'
        self.has_image = '' if has_image is False else '&hasPic=1'
        self.posted_today = '' if posted_today is False else '&postedToday=1'

    def _sites(self):
        self.sac.driver
    
        
    def _get_geos(self,geo_location_url=None):    
        self.sites_url = "https://www.craigslist.org/about/sites#US" if  geo_location_url is None else geo_location_url
        old_url = self.driver.current_url
        self.goto(self.sites_url)
        
        xp_a = "//h1/a[@name='US']/following::div/div/ul/li/a"
        a_elems = self.driver.find_elements_by_xpath(xp_a)
        hrefs = []
        geos = []
        for a_elem in a_elems:
            try:
                hrefs.append(a_elem.get_attribute("href"))
                geos.append(a_elem.text.encode('UTF-8'))
            except Exception:
                traceback.print_exc()
                
        df = pd.DataFrame({'href':[str(s) for s in hrefs],'text':geos})
        self.driver.get(old_url)
        return df
    
    
        
    def main(self):
        self.logger.info("ca_main starting %04d - %4d time %s" %(int(str(self.beg_geo_index)),int(str(self.end_geo_index)), str(datetime.datetime.now())))
        href_array = []
        text_array = []
        geo_name_array = []
        date_posted_array = []
        date_updated_array = []
    #     price_array = []
        
        dict_df = {}    
        output_file_path = self.output_folder_path + "/craigs_list_search_results_%02d_%02d.csv" %(self.beg_geo_index,self.end_geo_index) 
        for i in range(self.beg_geo_index,self.end_geo_index+1):
            row = self.df_geos.iloc[i]
            geo = row.href
            geo_name = row.text.replace(' ','_')
            
            make_model = self.make
            if self.model is not None:
                make_model = self.make+"+" + str(self.model)
            d = {
                 '_GEO':geo,
                 '_Q':str(make_model),
#                  '_SD':str(search_distance),
                 '_MINOD':str(self.min_auto_miles),
                 '_MAXOD':str(self.max_auto_miles),
                 '_MAY': str(self.max_auto_year),
                 '_AT': str(self.auto_transmission),
                 '_TO':self.titles_only,
                 '_HIM':self.has_image,
                 '_PT':self.posted_today
                 }
            
            base_url = "%(_GEO)ssearch/cta?auto_make_model=%(_Q)s&sort=date&max_auto_year=%(_MAY)s&auto_transmission=%(_AT)s&min_auto_miles=%(_MINOD)s&max_auto_miles=%(_MAXOD)s"
            url = base_url %d
            self.goto(url)
            a_link_array  = self.driver.find_elements_by_xpath("//a[@class='result-title hdrlnk']")
            
            for href in [s.get_attribute("href") for s in a_link_array]:
                try:
                    self.logger.info("processing href: " + str(href))
                    self.driver.get(href)
                    t = self.driver.find_element_by_xpath("//section[@id='postingbody']").text.encode('UTF-8')
                    try:
                        h = str(href)
                    except:
                        h = href.encode('UTF'-8)
                    href_array.append(h)
    #                 ts = str(t).replace('\n','\\n')
                    ts = t.decode("utf-8").replace('\n','\\n').replace(',',';')
                    text_array.append(ts)
                    geo_name_array.append(geo_name)
                    date_posted = ''
                    date_updated = ''
                    try:
                        date_posted = self.driver.find_element_by_xpath('//div[@class="postinginfos"]/p[contains(text(),"posted")]/time[@class="date timeago"]').get_attribute('datetime').encode('UTF-8')
                        date_posted = re.findall('2[0-1][0-9]{2}[-][0-1][0-9][-][[0-3][0-9]',date_posted)[0]
                        date_updated = self.driver.find_element_by_xpath('//div[@class="postinginfos"]/p[contains(text(),"updated")]/time[@class="date timeago"]').get_attribute('datetime').encode('UTF-8')
                        date_updated = re.findall('2[0-1][0-9]{2}[-][0-1][0-9][-][[0-3][0-9]',date_updated)[0]
                    except:
                        pass
                    date_posted_array.append(date_posted)
                    date_updated_array.append(date_updated)
                    for key in DICT_CRAIG_ACCESS_ATTRIBUTES_XPATH.keys():                    
                        try:
                            if key not in dict_df:
                                dict_df[key] = []
                            p = self.driver.find_element_by_xpath(DICT_CRAIG_ACCESS_ATTRIBUTES_XPATH[key]).text.encode('UTF-8')
    #                         ps = p.replace('\n','\\n') 
                            ps = p.decode("utf-8").replace('\n','\\n').replace(',',';')
                            dict_df[key].append(ps)
                        except:
                            dict_df[key].append('')
                except Exception as e:
                    traceback.print_exc()
        dict_df['href'] = href_array
        dict_df['page_text'] = text_array
        dict_df['geo'] = geo_name_array
        dict_df['date_posted'] = date_posted_array
        dict_df['date_updated'] = date_updated_array
        
    #     df = pd.DataFrame({'href':href_array,'text':text_array,'geo':geo_name_array,'price':price_array,'title':title_array})
        df = pd.DataFrame(dict_df)
        self.logger.info('ca_main saving csv file to ' + str(output_file_path))
        df.to_csv(output_file_path,index=False)
        self.logger.info("ca_main stopping %04d - %4d time %s" %(int(str(self.beg_geo_index)),int(str(self.end_geo_index)), str(datetime.datetime.now())))
        return df

if __name__=='__main__':
    '''
    # Example python command arguments
    --beg_geo_index 0
    --end_geo_index None # use all geos
    --output_folder_path ./temp_folder
    --make BMW
    --model 2002
    --max_auto_year 2001
    --headless False
    
    ca = CraigAccess(
        headless=headless, 
        geos_csv_path=geos_csv_path,
        beg_geo_index=beg_geo_index, 
        end_geo_index=end_geo_index, 
        output_folder_path=output_folder_path, 
        make=make, 
        model=model, 
        max_auto_year=max_auto_year)
    ca.main()
    '''
    
    parser = sac.gpar()
    parser.add_argument("--geos_csv_path",type=str,
               help="path to csv file containing geo locations",
               default="./df_geos.csv")
    parser.add_argument("--geo_index_low",type=int,
               help="low index of df_geo to start looping through geos",
               default=0)
    parser.add_argument("--geo_index_high",type=int,
               help="high index of df_geo to start looping through geos",
               nargs="?")
    parser.add_argument("--output_folder_path",type=str,
               help="output file path to store results",
               default="./temp_folder")
    parser.add_argument("--make",type=str,
               help="car make, like BMW",
               default="BMW")

    parser.add_argument("--model",type=str,
               help="car model, like 2002",
               nargs="?")
    
    parser.add_argument("--search_distance",type=int,
               help='search_distance parameter in Craigs list',
               default="200")
    parser.add_argument("--postal",type=str,
               help='zip code (postal) parameter in Craigs list',
               default="06824")
    parser.add_argument("--min_auto_miles",type=int,
               help='min_auto_miles parameter in Craigs list',
               default=0)
    parser.add_argument("--max_auto_miles",type=int,
               help='max_auto_miles parameter in Craigs list',
               default=500000)
    parser.add_argument("--max_auto_year",type=int,
               help='max_auto_year parameter in Craigs list',
               default=2100)
    
    parser.add_argument("--auto_transmission",type=int,
               help='auto_transmission parameter in Craigs list (1 = manual, 2=automatic)  Default = 1',
               default="1")    
    parser.add_argument("--headless",type=str,
               help="run in headless (don't show browser) mode",
               nargs="?")
    parser.add_argument("--titles_only",type=bool,
               help="only search the title field",
               default=False)
    parser.add_argument("--has_image",type=bool,
               help="only find matches that have images",
               default=False)
    parser.add_argument("--posted_today",type=bool,
               help="only find matches that were posted today",
               default=False)

    args = parser.parse_args() 
       
    logger = sac.lfa(args)
#     print ca.df_geos

    geos_csv_path = args.geos_csv_path
    make=args.make
    model=args.model
    search_distance=int(args.search_distance)
    postal=args.postal
    max_auto_year=args.max_auto_year
    auto_transmission=args.auto_transmission

    
    beg_geo_index = args.geo_index_low
    end_geo_index = args.geo_index_high
    output_folder_path = args.output_folder_path
    headless = args.headless
    min_auto_miles = args.min_auto_miles
    max_auto_miles = args.max_auto_miles
    titles_only = args.titles_only
    has_image = args.has_image
    posted_today = args.posted_today
    
    ca = CraigAccess(
        headless=headless, 
        geos_csv_path=geos_csv_path,
        beg_geo_index=beg_geo_index, 
        end_geo_index=end_geo_index, 
        output_folder_path=output_folder_path, 
        make=make, 
        model=model, 
        max_auto_year=max_auto_year, 
        min_auto_miles=min_auto_miles, 
        max_auto_miles=max_auto_miles, 
        auto_transmission=auto_transmission, 
        titles_only=titles_only, 
        has_image=has_image, 
        posted_today=posted_today)
    ca.main()
        

