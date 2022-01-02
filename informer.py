import logging
import requests
import schedule
import time
import configparser
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


config = configparser.ConfigParser()  # создаём объекта парсера
config.read("settings.ini")  # читаем конфиг
token = config['Telegramm']['token']
channel_id = config['Telegramm']['channel_id']
work_dir = config['Telegramm']['work_dir']
ping = int(config['Telegramm']['ping'])

logging.basicConfig(filename=work_dir + 'info.log', level=logging.DEBUG, format='%(asctime)s %(message)s')



def send_message(link, token, channel_id):
    url = "https://api.telegram.org/bot"
    #channel_id = "-450216618"
    #channel_id = '-638259980'
    url += token
    method = url + "/sendMessage"

    for i in range(3):
        r = requests.post(method, data={
            "chat_id": channel_id,
            "text": 'На Makeready был добавлен новый ружейный матч:' + '\n' + 'https://makeready.ru' + link
            })

        if r.status_code == 200:
            break
        time.sleep(60)
    else:
        logging.warning('Post error:', r.status_code)
    
    return r.status_code



def job(token, channel_id):
    
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
                    send_message(link, token, channel_id)
            f.close()

        with open(work_dir + 'links.txt', 'w', encoding='utf-8') as f:
            for match in shotgun_matches:
                f.write(match.find('a')['href']+'\n')
            f.close()

logging.warning(ping)
schedule.every(ping).minutes.do(job, token=token, channel_id=channel_id)

while True:
    schedule.run_pending()
    time.sleep(1)    

