import time
import configparser
import os
import logging
import shelve
import schedule
from bs4 import BeautifulSoup
import requests

BASE_LINK = "https://www.makeready.ru"

work_dir = os.path.dirname(os.path.realpath(__file__)) + '/'
AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0'

config = configparser.ConfigParser()
config.read(work_dir + 'settings.ini')
channel_id = config['Telegramm']['channel_id']
token =  config['Telegramm']['token']
ping = int(config['Telegramm']['ping'])

method = 'https://api.telegram.org/bot'+ token + '/sendMessage'

logging.basicConfig(filename=work_dir + 'info.log', level=logging.DEBUG,
                    format='%(asctime)s %(message)s')


def check_briefing(link: str):

    try:
        response = requests.get(BASE_LINK + link, headers={'User-Agent': AGENT})
        if response.status_code == 200:
            bsoup = BeautifulSoup(response.text, 'lxml')
            brief_links = bsoup.find('a', string='Брифинги')
            if not brief_links is None:
                brief_links = brief_links['href']
            return brief_links
        return None

    except Exception as exc:
        logging.error(exc, exc_info=True)


def send_message(text: str):

    for _ in range(3):
        response = requests.post(method, data={
            "chat_id": channel_id,
            "text": text,
            })
        if response.status_code == 200:
            break
        time.sleep(5)
    else:
        logging.warning('Post error:', response.status_code)

    return response.status_code

def get_matches_list():

    response = requests.get(BASE_LINK, headers={'User-Agent': AGENT})
    if response.status_code == 200:
        bsoup = BeautifulSoup(response.text, 'lxml')
        scheduler = bsoup.find('table', class_='bordered scheduleTable')
        list_matches = scheduler.find_all('tr')
        shotgun_matches = []
        for each in list_matches[:-1]:
            tags = each['tags'].split(',')
            if tags[1] == 'shotgun' and tags[2] == 'ru':
                shotgun_matches.append(each)
        return shotgun_matches
    return None

def main_job():

    shotgun_matches = get_matches_list()

    if shotgun_matches is None:
        return

    with shelve.open(work_dir + 'base_test.db', flag='c') as matches_dict:
        for match in shotgun_matches:
            link =  match.find('a')['href']
            if not link in matches_dict.keys():
                send_message('На Makeready был добавлен новый ружейный матч:' +
                '\n' + BASE_LINK + link)
                matches_dict[link] = -1
            if matches_dict[link] == -1:
                brief_link = check_briefing(link)
                if not brief_link is None:
                    matches_dict[link] = brief_link
                    send_message('Для матча ' +
                        BASE_LINK + link + '\n' + 'появился брифинг: ' +
                        '\n' + BASE_LINK + brief_link)
        matches_dict.close()

schedule.every(ping).minutes.do(main_job)


while True:
    schedule.run_pending()
    time.sleep(1)
