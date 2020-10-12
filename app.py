import os
import csv
import time
import telepot
import requests
import unidecode
import constants
from decouple import config
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from telepot.loop import MessageLoop

TOKEN = config('TOKEN')
NfceBot = telepot.Bot(TOKEN)

def start(chatId):
    NfceBot.sendMessage(chatId, constants.MSG_START)

def error_command(chatId):
    NfceBot.sendMessage(chatId, constants.MSG_ERROR_COMMAND)

def error_url_invalid(chatId):
    NfceBot.sendMessage(chatId, constants.MSG_URL_INVALID)

def error_handler(chatId):
    NfceBot.sendMessage(chatId, constants.MSG_ERROR_HANDLER)

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

def generate_spreadsheet(nameFile, data):
    if os.path.exists(nameFile):
        os.remove(nameFile)

    file = open(nameFile, 'a', encoding='utf-8')

    file.write('ESTABLISHMENT' + ';' + data['establishment'] + '\n')
    file.write('DATE' + ';' + data['date'] + '\n')
    file.write('\n')
    file.write('NAME' + ';' + 'CODE' + ';' + 'AMOUNT' + ';' + 'UNITARY VALUE' + ';' + 'TOTAL' +'\n')

    for product in data['products']:
        file.write(
            product['name'] + ';' +
            product['code'] + ';' +
            product['amount'] + ';' +
            product['unitaryValue'] + ';' +
            product['total'] +'\n'
        )

    file.close()

def send_document(chatId, nameFile):
    NfceBot.sendDocument(chatId, open(nameFile, 'rb'))    
    
def handler(msg):
    try:
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type == 'text':
            if msg['text'] == '/start':
                start(chat_id)
            else:
                if url_validator(msg['text']):
                    data = scraper(msg['text'])

                    if data:
                        nameFile = data['establishment'] + '-' + data['date']
                        nameFile = nameFile.replace(' ', '-')
                        nameFile = nameFile.replace('/', '-')
                        nameFile = nameFile.lower()
                        nameFile = unidecode.unidecode(nameFile)
                        nameFile = nameFile + '.csv'

                        generate_spreadsheet(nameFile, data)
                        send_document(chat_id, nameFile)
                else:
                    error_url_invalid(chat_id)
        else:
            error_command(chat_id)
    except:
        error_handler(chat_id)



MessageLoop(NfceBot, handler).run_as_thread()
print ('Listening ...')


while 1:
    time.sleep(10)
