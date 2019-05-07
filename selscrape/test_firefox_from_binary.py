'''
Created on May 07, 2019
Test running a firefox binary which downloads a pdf from a page that
  has an href to the pdf

example args for mac:
    --firefox_binary_path /Applications/Firefox.app/Contents/MacOS/firefox 
    --executable_path ../../selscrape/selscrape/drivers/geckodriver_mac

example args for linux (these are the program defaults):
   --is_headless False
   
    --firefox_binary_path /root/firefox_binary/opt/firefox/firefox 
    --executable_path ../../selscrape/selscrape/drivers/geckodriver_linux

example args for linux (If your installed version of firefox is 62.0.2 or greater):
    --firefox_binary_path /usr/bin/firefox 
    --executable_path ../../selscrape/selscrape/drivers/geckodriver_linux

@author: bperlman1
'''
import os
import time
from selscrape import sel_scrape as sela
import argparse as ap

if __name__ == '__main__':
    parser = ap.ArgumentParser()

    parser.add_argument('--firefox_profile_path',type=str,
                        help="path to firefox profile folder",
                        default="../../eincreator/eincreator/configs/firefox_profile")
    parser.add_argument('--is_headless',type=str,
                        help="True if headless, else False (default)",
                        default="False")
    
    parser.add_argument('--url_with_download_link',type=str,
                        help="Url of page that has an href with a pdf to download",
                        default="https://www.irs.gov/forms-pubs/about-form-1040")
    parser.add_argument('--xpath_to_pdf_download',type=str,
                        help="xpath to link that has an href with a pdf to download",
                        default='//a[@href="https://www.irs.gov/pub/irs-pdf/f1040.pdf"]')
    
    parser.add_argument('--firefox_binary_path',type=str,
                        help="path to firefox binary",
                        default='/root/firefox_binary/opt/firefox/firefox')
    parser.add_argument('--executable_path',type=str,
                        help="xpath to proper geckodriver or chrome driver per operating system",
                        default='../../selaccess/selaccess/drivers/geckodriver_linux')

    args = parser.parse_args()
    firefox_profile_path = args.firefox_profile_path
    is_headless = str(args.is_headless).lower()=="true"
    url_with_download_link = args.url_with_download_link
    xpath_to_pdf_download = args.xpath_to_pdf_download
    firefox_binary_path = args.firefox_binary_path
    executable_path = args.executable_path
    
    df = os.path.abspath('./temp_folder')
#     ff_bin = '/Applications/Firefox.app/Contents/MacOS/firefox'
    pp = os.path.abspath(firefox_profile_path)
    sac = sela.SelScrape(driver_name='firefox_from_binary',executable_path=executable_path,
                         firefox_binary_path=firefox_binary_path,
                         headless=is_headless,download_folder=df,profile_path=pp)
    time.sleep(2)
    sac.goto(url_with_download_link)
    time.sleep(2)
    sac.click_element(xpath_to_pdf_download)
    time.sleep(2)
    sac.driver.quit()
