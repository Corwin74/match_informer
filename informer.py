import logging
import requests
import schedule
import time
from bs4 import BeautifulSoup
from fake_useragent import UserAgent



WORK_DIR = '/home/sysadmin/match_informer/match_informer/'

logging.basicConfig(filename=WORK_DIR + 'info.log', level=logging.DEBUG, format='%(asctime)s %(message)s')



def send_message(link):
    token = "5098599229:AAHqtLpW4-0v9-XTNJZiOLQ6lGyNnI6xDsE"
    url = "https://api.telegram.org/bot"
    #channel_id = "-450216618"
    channel_id = '-638259980'
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

schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)    

