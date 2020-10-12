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
    print(soup)

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
