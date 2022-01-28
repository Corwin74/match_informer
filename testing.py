import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent, FakeUserAgentError
import shelve
import os


work_dir = os.path.dirname(os.path.realpath(__file__)) + '/'

with shelve.open(work_dir + 'base_test.db', flag='c') as match_dict:
    match_dict['https://mothefaucker'] = -3
    match_dict.close()


with shelve.open(work_dir + 'base_test.db', flag='c') as match_dict:
    for key in match_dict.keys():
        print(key)