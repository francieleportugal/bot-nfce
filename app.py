import time
import telepot
import requests
from decouple import config
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from telepot.loop import MessageLoop
import constants
import unidecode

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
    data = {
        'establishment': None,
        'date': None,
        'products': [],
    }

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    establishment = soup.find('div', attrs={'class': 'txtTopo'})

    if establishment:
        data['establishment'] = establishment.get_text()
    
    infoGeneral = soup.find('ul')

    for strongTag in infoGeneral.find_all('strong'):

        # Normalize text
        strongTagText = strongTag.text
        strongTagText = strongTagText.replace(' ', '')
        strongTagText = strongTagText.replace(':', '')
        strongTagText = strongTagText.lower()
        strongTagText = unidecode.unidecode(strongTagText)

        if strongTagText == 'emissao':
            data['date'] = strongTag.next_sibling.split(' ')[0]

    table = soup.find('table', attrs={'id': 'tabResult'})
    rows = table.findAll('tr')

    for row in rows:
        product = {
            'name': None,
            'code': None,
            'amount': None,
            'unitaryValue': None,
            'total': None,
        }

        cols = row.find_all('td')

        for tag in cols:
            name = tag.find('span', attrs={'class': 'txtTit'})
            code = tag.find('span', attrs={'class': 'RCod'})
            amount = tag.find('span', attrs={'class': 'Rqtd'})
            unitaryValue = tag.find('span', attrs={'class': 'RvlUnit'})
            total = tag.find('span', attrs={'class': 'valor'})

            if name:
                product['name'] = name.get_text()
            if code:
                product['code'] = code.get_text().split(':')[1].split(')')[0]
            if amount:
                product['amount'] = amount.get_text().split(':')[1]
            if unitaryValue:
                product['unitaryValue'] = unitaryValue.get_text().split(':')[1]            
            if total:
                product['total'] = total.get_text()
        
        data['products'].append(product)

    return data


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
