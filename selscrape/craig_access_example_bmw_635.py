'''
Created on May 10, 2019

@author: bperlman1
'''
from selscrape import craig_access as ca
import datetime

if __name__ == '__main__':
    print(f'start search at {datetime.datetime.now()}')
    ca_bmw_635 = ca.CraigAccess(headless=False,
            make='BMW',
            model='635',
            geos_csv_path='df_geos_houston.csv')
    ca_bmw_635.main()
    print(f'end search at {datetime.datetime.now()}')    