import logging
import requests
import os
from bs4 import BeautifulSoup
from requests.sessions import should_bypass_proxies
from fake_useragent import UserAgent

WORK_DIR = '/home/alex/projects/match_informer/'

def send_message(link):
    print('Новый матч', link)

logging.basicConfig(filename=WORK_DIR + 'info.log', level=logging.DEBUG, format='%(asctime)s %(message)s')
logging.warning('is when this event was logged.')

response = requests.get("https://www.makeready.ru/", headers={'User-Agent': UserAgent().random})
if response.status_code == 200:
    bs = BeautifulSoup(response.text, 'lxml')
    scheduler = bs.find('table', class_='bordered scheduleTable')
    list_matches = scheduler.find_all('tr')
    shotgun_matches = []
    for each in list_matches[:-1]:
        if each['tags'].split(',')[1] == 'shotgun':
            shotgun_matches.append(each)
else:
    print(response.status_code)
base_list = []

with open(WORK_DIR + 'links.txt', 'r', encoding='utf-8') as f:
    for line in f:
        base_list.append(line.rstrip())
    for match in shotgun_matches:
        link =  match.find('a')['href']
        if not link in base_list:
            send_message(link)
    f.close()
with open(WORK_DIR + 'links.txt', 'w', encoding='utf-8') as f:
    for match in shotgun_matches:
        f.write(match.find('a')['href']+'\n')
    f.close()


         

