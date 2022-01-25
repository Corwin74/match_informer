import logging
from xmlrpc.client import Boolean
import requests
import schedule
import time
import configparser
from bs4 import BeautifulSoup
from fake_useragent import UserAgent, FakeUserAgentError
import os

config = configparser.ConfigParser()  # создаём объекта парсера
config.read("/home/alex/projects/match_informer/settings_test.ini")  # читаем конфиг
channel_id = config['Telegramm']['channel_id']
token =  config['Telegramm']['token']
ping = int(config['Telegramm']['ping'])

try:
    ua = UserAgent(fallback='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0')
    agent = ua.random
except FakeUserAgentError:
    print('Bebe1')

work_dir = os.path.dirname(os.path.realpath(__file__)) + '/'

logging.basicConfig(filename=work_dir + 'info.log', level=logging.DEBUG, format='%(asctime)s %(message)s')


def check_briefing(link: str):

    try:
        response = requests.get(link, headers={'User-Agent': agent})
        if response.status_code == 200:
            bs = BeautifulSoup(response.text, 'lxml')
        return bs.find('a', string='Брифинги')
    except:
        return False

def send_message(text: str):
    url = "https://api.telegram.org/bot"
    url += token
    method = url + "/sendMessage"

    for i in range(3):
        r = requests.post(method, data={
            "chat_id": channel_id,
            "text": text,
            })

        if r.status_code == 200:
            break
        time.sleep(60)
    else:
        logging.warning('Post error:', r.status_code)
    
    return r.status_code


def job():
    
    response = requests.get("https://www.makeready.ru/", headers={'User-Agent': UserAgent().random})
    if response.status_code == 200:
        bs = BeautifulSoup(response.text, 'lxml')
        scheduler = bs.find('table', class_='bordered scheduleTable')
        list_matches = scheduler.find_all('tr')
        shotgun_matches = []
        for each in list_matches[:-1]:
            t = each['tags'].split(',')
            if t[1] == 'shotgun' and t[2] == 'ru':
                shotgun_matches.append(each)

    base_list = []

    with open(work_dir + 'links.txt', 'r', encoding='utf-8') as f:
        for line in f:
            base_list.append(line.rstrip())
        for match in shotgun_matches:
            link =  match.find('a')['href']
            if not link in base_list:
                send_message('На Makeready был добавлен новый ружейный матч:' + '\n' + 'https://makeready.ru' + link)
            x = check_briefing(link)
            if x == None or x == False:
                pass
            else:
                send_message('Брифинг мазафака!')
        f.close()

    with open(work_dir + 'links.txt', 'w', encoding='utf-8') as f:
        for match in shotgun_matches:
            f.write(match.find('a')['href']+'\n')
        f.close()

schedule.every(ping).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)    

