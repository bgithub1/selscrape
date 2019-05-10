'''
Created on May 10, 2019

@author: bperlman1
'''
from selscrape import craig_access as ca
import datetime

if __name__ == '__main__':
    print(f'start search at {datetime.datetime.now()}')
    ca_bmw_2002 = ca.CraigAccess(headless=False,
            make='BMW',
            model='2002',
            max_auto_year='1969', 
            max_auto_miles=300000)
    ca_bmw_2002.main()
    print(f'end search at {datetime.datetime.now()}')    