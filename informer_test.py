import logging
import requests
import schedule
import time
import configparser
from bs4 import BeautifulSoup
import os
import shelve

BASE_LINK = "https://www.makeready.ru"

work_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
agent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0'

config = configparser.ConfigParser()  
config.read(work_dir + 'settings_test.ini')  
channel_id = config['Telegramm']['channel_id']
token =  config['Telegramm']['token']
ping = int(config['Telegramm']['ping'])

method = 'https://api.telegram.org/bot'+ token + '/sendMessage'

logging.basicConfig(filename=work_dir + 'info.log', level=logging.DEBUG, format='%(asctime)s %(message)s')


def check_briefing(link: str):

    try:
        print('Check briefing', link)
        response = requests.get(BASE_LINK + link, headers={'User-Agent': agent})
        if response.status_code == 200:
            bs = BeautifulSoup(response.text, 'lxml')
            x = bs.find('a', string='Брифинги')
            if not x == None:
                x = x['href']
            return x
        else:
            return None
    except Exception as e:
        logging.warning('Exception:', e)



def send_message(text: str):
    
    print(method)
    for i in range(3):
        r = requests.post(method, data={
            "chat_id": channel_id,
            "text": text,
            })

        if r.status_code == 200:
            break
        time.sleep(5)
    else:
        logging.warning('Post error:', r.status_code)
    
    return r.status_code

def get_matches_list():
    
    response = requests.get(BASE_LINK, headers={'User-Agent': agent})
    if response.status_code == 200:
        bs = BeautifulSoup(response.text, 'lxml')
        scheduler = bs.find('table', class_='bordered scheduleTable')
        list_matches = scheduler.find_all('tr')
        shotgun_matches = []
        for each in list_matches[:-1]:
            t = each['tags'].split(',')
            if t[1] == 'shotgun' and t[2] == 'ru':
                shotgun_matches.append(each)
        return shotgun_matches
    return None

def main_job():
    
    shotgun_matches = get_matches_list()

    if shotgun_matches == None:
        return

    with shelve.open(work_dir + 'base_test.db', flag='c') as matches_dict:
        for match in shotgun_matches:
            link =  match.find('a')['href']
            if not link in matches_dict.keys():
                send_message('На Makeready был добавлен новый ружейный матч:' + '\n' + BASE_LINK + link)
                matches_dict[link] = -1
            if matches_dict[link] == -1:
                brief_link = check_briefing(link)
                if not brief_link == None:
                    matches_dict[link] = brief_link
                    send_message('Для матча ' + 
                        BASE_LINK + link + '\n' + 'появился брифинг: ' + '\n' + BASE_LINK + brief_link)
        matches_dict.close()

schedule.every(ping).minutes.do(main_job)


while True:
    schedule.run_pending()
    time.sleep(1)    

