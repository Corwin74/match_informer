import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent, FakeUserAgentError

try:
    ua = UserAgent(fallback='Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:21.0) Gecko/20100101 Firefox/21.0')
except FakeUserAgentError:
    pass
    
response = requests.get("https://www.makeready.ru/schedule/Chempionat-Sankt-Peterburga-po-prakticheskoj-strelbe-iz-ruzhya-17-11-2022-44281317012022/", 
                        headers={'User-Agent': ua.random})
if response.status_code == 200:
    bs = BeautifulSoup(response.text, 'lxml')
    scheduler = bs.find('a', string='Брифинги')
if scheduler == None:
    print('Брифингов нема')
else:
    print(scheduler)
