import telepot
from decouple import config

TOKEN = config('TOKEN')

TelegramBot = telepot.Bot(TOKEN)

print (TelegramBot.getMe())