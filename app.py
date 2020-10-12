import time
import telepot
import requests
from decouple import config
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from telepot.loop import MessageLoop
import constants

TOKEN = config('TOKEN')
NfceBot = telepot.Bot(TOKEN)

def start(chatId):
    NfceBot.sendMessage(chatId, constants.MSG_START)

def error_command(chatId):
    NfceBot.sendMessage(chatId, constants.MSG_ERROR_COMMAND)

def error_url_invalid(chatId):
    NfceBot.sendMessage(chatId, constants.MSG_URL_INVALID)

def url_validator(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path])
    except:
        return False

def scraper(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    table = soup.find('table', attrs={'id': 'tabResult'})
    rows = table.findAll('tr')

    data = []
    for row in rows:
        print ('------------------')
        cols = row.find_all('td')
        product = dict()

        for tag in cols:
            print ('product: ', product)
            product = dict()

            name = tag.find('span', attrs={'class': 'txtTit'})
            code = tag.find('span', attrs={'class': 'RCod'})
            amount = tag.find('span', attrs={'class': 'Rqtd'})
            unitaryValue = tag.find('span', attrs={'class': 'RvlUnit'})
            total = tag.find('span', attrs={'class': 'valor'})

            if name:
                print ('Name: ', name.get_text())
                product['name'] = name.get_text()
            if code:
                print ('Code: ', code.get_text().split(':')[1].split(')')[0])
                product['code'] = code.get_text().split(':')[1].split(')')[0]
            if amount:
                print ('Amount: ', amount.get_text().split(':')[1])
                product['amount'] = amount.get_text().split(':')[1]
            if unitaryValue:
                print ('Unitary Value: ', unitaryValue.get_text().split(':')[1])
                product['unitaryValue'] = unitaryValue.get_text().split(':')[1]
            if total:
                print ('total: ', total.get_text())
                product['total'] = total.get_text()
        

def handler(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == 'text':
        if msg['text'] == '/start':
            start(chat_id)
        else:
            if url_validator(msg['text']):
                scraper(msg['text'])
            else:
                error_url_invalid(chat_id)
    else:
        error_command(chat_id)



MessageLoop(NfceBot, handler).run_as_thread()
print ('Listening ...')


while 1:
    time.sleep(10)
