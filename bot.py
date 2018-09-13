# bot.py

#import random
#from io import BytesIO

import requests
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import subprocess

import json
import re
from secrets import *

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth)

addvert = 'Give and receive #cryptocurrency $AIQ from @artiqox - just tweet "giveaiq help" for more info. #AIQ #BTC'
bot_username = 'GiveAIQ'

def balance(user,tweetId,options):
    lowsymb = options.lower()
    uppsymb = options.upper()
    api_url = requests.get('https://api.coingecko.com/api/v3/coins/artiqox?localization=false')
    market_data_json = api_url.json()
    current_price_json = json.loads(json.dumps(market_data_json['market_data']))
    currency_json = json.loads(json.dumps(current_price_json['current_price']))
    if user is None:
        print("no user")
    else:
        if lowsymb in currency_json:
            fiat_price = json.dumps(currency_json[lowsymb])
            if lowsymb == 'btc':
                decplace = 8
            else:
                decplace = 4
        else:
            fiat_price = json.dumps(currency_json['usd'])
            uppsymb = "USD"
            decplace = 4
        core = "/home/osboxes/artiqox-ttbot/artiqox-1.1.2/artiqox-cli"
        result = subprocess.run([core,"getbalance","TT-" + user.lower()],stdout=subprocess.PIPE)
        clean = (result.stdout.strip()).decode("utf-8")
        balance  = float(clean)
        last_fiat = float(fiat_price)
        fiat_balance = balance * last_fiat
        fiat_balance = str(round(fiat_balance,decplace))
        balance =  str(round(balance,4))
        api.update_status('Hi @{0}, your current balance is: {1} AIQ ≈ {2}{3}. {4}'.format(user,balance,uppsymb,fiat_balance,addvert), tweetId)
    
def give(user,tweetId,amount,target,options):

    lowsymb = options.lower()
    uppsymb = options.upper()
    api_url = requests.get('https://api.coingecko.com/api/v3/coins/artiqox?localization=false')
    market_data_json = api_url.json()
    current_price_json = json.loads(json.dumps(market_data_json['market_data']))
    currency_json = json.loads(json.dumps(current_price_json['current_price']))
    core = "/home/osboxes/artiqox-ttbot/artiqox-1.1.2/artiqox-cli"
    result = subprocess.run([core,"getbalance","TT-" + user.lower()],stdout=subprocess.PIPE)
    balance = float((result.stdout.strip()).decode("utf-8"))
    if lowsymb in currency_json:
        fiat_price = json.dumps(currency_json[lowsymb])
        if lowsymb == 'btc' or lowsymb == 'aiq':
            decplace = 8
        else:
            decplace = 4
    else:
        fiat_price = 1.0
        uppsymb = "AIQ"
        decplace = 8

    last_fiat = float(fiat_price)
    fiat_balance = balance * last_fiat
    fiat_balance = str(round(fiat_balance,decplace))
    print(amount)
    amount = float(amount)
    amount_aiq = amount / last_fiat
    amount_aiq = float(amount_aiq)   
    if balance < amount_aiq:
        api.update_status('@{0} you have insufficent funds. {1}'.format(user,addvert), tweetId)
    elif target == user:
        api.update_status('@{0} you can\'t give yourself AIQ. {1}'.format(user,addvert), tweetId)
# what is min len for tt user name?
#    elif len(target) < 5:
#        api.update_status('Error that user is not applicable. Twitter requires users to have 5 or more characters in their @username.', tweetId)

    elif uppsymb == "AIQ":
        balance = str(balance)
        amount = str(amount)
        tx = subprocess.run([core,"move","TT-" + user.lower(),"TT-" + target.lower(),amount_aiq],stdout=subprocess.PIPE)
        api.update_status('Hi @{1}, @{0} gave you {2} AIQ. {3}'.format(user, target, amount_aiq, addvert), tweetId)
    else:
        balance = str(balance)
        amount = str(amount)
        amount_aiq = str(round(amount_aiq,decplace))
        tx = subprocess.run([core,"move","TT-" + user.lower(),"TT-" + target.lower(),amount_aiq],stdout=subprocess.PIPE)
        api.update_status('Hi @{1}, @{0} gave you {2} AIQ ≈ {3}{4}. {5}'.format(user, target, amount_aiq, uppsymb, amount, addvert), tweetId)

def deposit(user,tweetId,options):

    if options == "qr":
        address = "/home/osboxes/artiqox-ttbot/artiqox-1.1.2/artiqox-cli"
        result = subprocess.run([address,"getaccountaddress","TT-" + user.lower()],stdout=subprocess.PIPE)
        clean = (result.stdout.strip()).decode("utf-8")
        api.update_status('Hi @{0}, your depositing address is: {1} follow https://chart.googleapis.com/chart?cht=qr&chl=artiqox%3A{1}&chs=180x180&choe=UTF-8&chld=L|2 to get your QR code. {2}'.format(user, clean, addvert), tweetId)

    else:
        address = "/home/osboxes/artiqox-ttbot/artiqox-1.1.2/artiqox-cli"
        result = subprocess.run([address,"getaccountaddress","TT-" + user.lower()],stdout=subprocess.PIPE)
        clean = (result.stdout.strip()).decode("utf-8")
        api.update_status('Hi @{0}, your depositing address is: {1} {2}'.format(user, clean, addvert), tweetId)

def withdraw(user,tweetId,amount,target):

    address = ''.join(str(e) for e in target)
    
    amount = float(amount)
    core = "/home/osboxes/artiqox-ttbot/artiqox-1.1.2/artiqox-cli"
    result = subprocess.run([core,"getbalance","TT-" + user.lower()],stdout=subprocess.PIPE)
    clean = (result.stdout.strip()).decode("utf-8")
    balance = float(clean)
    if balance < amount:
        api.update_status('Hi @{0}, you have insufficent funds. {1}'.format(user,addvert), tweetId)
    else:
        amount = str(amount)
        tx = subprocess.run([core,"sendfrom","TT-" + user.lower(),address,amount],stdout=subprocess.PIPE)
        api.update_status('@{0} has successfully withdrew to address: {1} of {2} AIQ. {3}'.format(user,address,amount,addvert), tweetId)

def help(user,tweetId,options):

    if options == "pl":

        api.update_status('Hi @{0}, give $AIQ by simply replying to anybody with "giveaiq 1.5" to give him 1.5 AIQ. You can also tweet "giveaiq @user 1.5" to give @user 1.5 AIQ. Tweet "giveaiq deposit" to see your deposit address, "giveaiq balance" to see your current balance.'.format(user), tweetId)

    else:

        api.update_status('Hi @{0}, give AIQ by simply replying to anybody with "giveaiq 1.5" to give him 1.5 AIQ. You can also tweet "giveaiq @user 1.5" to give @user 1.5 AIQ. Tweet "giveaiq deposit" to see your deposit address, "giveaiq balance" to see your current balance.'.format(user), tweetId)

# create a class inheriting from the tweepy  StreamListener
class BotStreamer(tweepy.StreamListener):
    # Called when a new status arrives which is passed down from the on_data method of the StreamListener
    def on_data(self, data):
        d = json.loads(data)
        user = d['user']['screen_name']
        tweetId = d['id']

        # give in case when user replies to somebody        
        pattern = r".*@" + re.escape(bot_username) + r" ([\d]+[\.]{0,1}[\d]*)\s*([a-zA-Z\d]{0,3}).*"
        match = re.match(pattern,d['text'])
        if d['in_reply_to_screen_name'] != "None" and user != bot_username and match:
            give(user,tweetId,match.group(1),d['in_reply_to_screen_name'],match.group(2))
        # give in case when user types giveaiq @targetUser amount
        pattern = r".*@" + re.escape(bot_username) + r" @([\w]+)\s*([\d]*[\.]{0,1}[\d]*)\s*([a-zA-Z\d]{0,3}).*"
        match = re.match(pattern,d['text'])
        if match and user != bot_username:
            give(user,tweetId,match.group(2),match.group(1),match.group(3))
        # withdraw of funds
        pattern = r".*@" + re.escape(bot_username) + r" withdraw \b([a-z\dA-Z]{34})\b (\d+[\.]*[\d]*)\s*"
        match = re.match(pattern,d['text'])
        if match and user != bot_username:
            withdraw(user,tweetId,match.group(2),match.group(1))
        # user checks balance
        pattern = r".*@" + re.escape(bot_username) + r" (balance)\s*([\w]*).*"
        match = re.match(pattern,d['text'])
        if match and user != bot_username:
            balance(user,tweetId,match.group(2))
        # user checks deposit
        pattern = r".*@" + re.escape(bot_username) + r" (deposit)\s*([\w]*).*"
        match = re.match(pattern,d['text'])
        if match and user != bot_username:
            deposit(user,tweetId,match.group(2))
        # user needs help
        pattern = r".*@" + re.escape(bot_username) + r" (help)\s*([\w]*).*"
        match = re.match(pattern,d['text'])
        if match and user != bot_username:
            help(user,tweetId,match.group(2))

myStreamListener = BotStreamer()
# Construct the Stream instance
stream = tweepy.Stream(auth, myStreamListener)
track_me='@'+bot_username
stream.filter(track=[track_me])
