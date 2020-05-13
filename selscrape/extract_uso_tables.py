'''
Created on Apr 26, 2020

@author: bperlman1
'''

from selscrape import sel_scrape as sc #@UnresolvedImport 
import pandas as pd
import sys
import re
import datetime

def get_pending_trades():
    sela = sc.SelScrape(driver_name='chrome',headless=True)
    sela.goto('http://www.uscfinvestments.com/holdings/uso')
    sela.wait_implicitly(10)
    xpath = "//span[@class='asofdate']"
    elem = sela.findxpath(xpath)
    asof_date_text = re.findall('[0-1][0-9]/[0-3][0-9]/2[0-1][0-9]{2}', elem['value'][0].text)[0]
    asof_dt = datetime.datetime.strptime(asof_date_text,'%m/%d/%Y')
    yyyymmdd = int(asof_dt.year)*100*100 + int(asof_dt.month)*100 + int(asof_dt.day)
    
    xpath = "//table[@id='pendingTradesTableID']"
    elem = sela.findxpath(xpath)
    
    text = elem['value'][0].text
    bs = 'buy'
    contracts = []
    sizes = []
    prices = []
    
    for line in text.split('\n'): 
        if not (('buy' in line.lower()) or ('sell' in line.lower())):
            continue       
        if 'sell' in line.lower():
            bs = 'sell'
        contract_and_data = line.lower().split(bs)
        contract = contract_and_data[0].strip().split(' ')[-1]
        data = contract_and_data[1].strip().split(' ')
        contracts.append(contract)
        size = int(data[0].replace(',',''))
        sizes.append(size)
        prices.append(round(float(data[1]),4))
    df = pd.DataFrame({'contract':contracts,'lots':sizes,'price':prices})
    df['yyyymmdd'] = yyyymmdd
    return df
    
if __name__== '__main__':
    save_name = None if len(sys.argv)<2 else sys.argv[1]
    df = get_pending_trades()
    
    if save_name is not None:
        df.to_csv(save_name)
    else:
        print(df)
        print(f"total dollars rolled = {sum(df.lots*df.price)}")
    
         
