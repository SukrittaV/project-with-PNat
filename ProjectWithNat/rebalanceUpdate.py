import hashlib
import hmac
import json
import requests
from time import time, sleep
from datetime import datetime
import configparser
from songline import Sendline 

### อ่านค่า line token ### 
token = global_config_val['line_token']
messenger = Sendline(token)

# API info
API_HOST = 'https://api.bitkub.com'

# TIME = 3600 #เวลาเช็คทุกๆ 1 ชั่วโมง

global_config_val = {}
config = configparser.ConfigParser()

def read_config():
    global config
    config.read("config.ini")
    global global_config_val
    global_config_val = config['CONFIG']
    
## อ่านค่า config ##
read_config()
last_price = global_config_val['last_price']

def timer(seconds): #ตัวนับเวลาถอยหลัง 
    total = 0
    while True:
        total = total + seconds
        sleep(seconds - time() % seconds)
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        rebalance_process()
        report()

def json_encode(data):
	return json.dumps(data, separators=(',', ':'), sort_keys=True)

def sign(data):
	j = json_encode(data)
	# print('Signing payload: ' + j)
	h = hmac.new(bytes(global_config_val['api_secret'], encoding='utf-8'), msg=j.encode(), digestmod=hashlib.sha256)
	return h.hexdigest()

# check server time
response = requests.get(API_HOST + '/api/servertime')
ts = int(response.text)
# print('Server time: ' + response.text)

# check balances
header = {
	'Accept': 'application/json',
	'Content-Type': 'application/json',
	'X-BTK-APIKEY': global_config_val['api_key'],
}
data = {
	'ts': ts,
}
signature = sign(data)
data['sig'] = signature

# def symbol_bitkub(): #ตรวจสอบสัญลักษณ์คู่เทรด
#     response = requests.get(API_HOST + '/api/market/symbols')
#     print (response.text) 
    
def ticker(coin = '', variable = ''): #หาราคาต่าง ๆ ของคู่เหรียญที่เราต้องการบอกราคาล่าสุด สูง ต่ำ เปอร์ที่เปลี่ยนแปลง 
    response = requests.get(API_HOST + '/api/market/ticker',params='sym='+coin) 
    responseJson = json.loads(response.text) #ต้องใช้ Load เพื่อให้สามารถเอาตัวแปรเข้ามาใช้งานได้จริง 
    result = ''
    if (variable == ''):
        result = responseJson[coin]
    else:
        result = responseJson[coin][variable]
    # print (result)
    return result
    
def check_balance():
    # print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/balances', headers=header, data=json_encode(data))
    # print (response.text)

def check_order():
    data = {
	'sym': global_config_val['trade_sym'], #คู่ที่เราจะเทรด ควร Config ได้
    'p' : 1,
    'lmt' :1,
	'ts': ts, #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature
    # print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/my-order-history',headers=header, data=json_encode(data)) 
    responseJson = json.loads(response.text) #ต้องใช้ Load เพื่อให้สามารถเอาตัวแปรเข้ามาใช้งานได้จริง 
    return responseJson['result'][0]['rate']
    
def sell_fiat(signal_sell): #ขายจำนวนเงินบาทที่ต้องการ ได้ใช้แน่ ๆ
    global last_price 
    data = {
	'sym': global_config_val['trade_sym'], #คู่ที่เราจะเทรด
	'amt': signal_sell, # BTC amount you want to sell
	'rat': 0, #ราคาที่ต้องการจะเข้าขาย
	'typ': 'market', #รูปแบบที่จะเทรด
	'ts': ts, #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature
    # print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/place-ask-by-fiat', headers=header, data=json_encode(data))
    print (response.text)
    last_price = check_order() 
    config.set('CONFIG', 'last_price', str(last_price))
    with open('config.ini', 'w') as f:
        config.write(f)

def buy(signal_buy): #ใช้ในการตั้งราคาซื้อ 
    global last_price
    data = {
	'sym': global_config_val['trade_sym'], #คู่ที่เราจะเทรด
	'amt': signal_buy, # THB amount you want to spend
	'rat': 0, #ราคาที่ต้องการจะเข้าซื้อ 
	'typ': 'market', #รูปแบบที่จะเทรด หากใช้ market จะเป็นเอาราคาปัจจุบันเลย
	'ts': ts, #ต้องมีติดไว้ทุกอันที่ใช้ Post
    }
    signature = sign(data)
    data['sig'] = signature
    
    print('Payload with signature: ' + json_encode(data))
    response = requests.post(API_HOST + '/api/market/place-bid', headers=header, data=json_encode(data))
    print (response.text)
    last_price = check_order() 
    config.set('CONFIG', 'last_price', str(last_price))
    with open('config.ini', 'w') as f:
        config.write(f)

def CheckAPIBitkub(): #เช็ค API ว่าทำงานได้ไหม 
    
    if showError == 0 :  
        print("------------------------------")
        print("-- Welcome to Rebalance BOT --")
        print("Bitkub API Checking : ok ")

    else:
        print("--------------------------------")
        print("Bitkub API Checking : Error!!!!! ")
        print("Please recheck your API . . . ")
        print("----------------------------------")

def report(): # รายงานสรุปผล
    print ('จำนวนเหรียญ'+ asset_sym +'ที่มี :', amount_asset )
    print ('จำนวนเงินบาทที่มี :', bath_balance )
    print ('มูลค่าพอร์ตโดยรวม :' , (amount_asset * price_now) + bath_balance , 'บาท') 
    report_txt = (f'จำนวนเหรียญ {asset_sym} ที่มี :, {amount_asset}\n จำนวนเงินบาทที่มี :, {bath_balance} \n มูลค่าพอร์ตโดยรวม :, {(amount_asset * price_now) + bath_balance} , บาท')
    messenger.sendtext(report_txt)

def rebalance_process(): #ขั้นตอนในการ Reblalnce 
    global last_price
    diffchange = (((price_now - last_price)/last_price)*100)
    print ('Diff :' , diffchange )
    diff_txt = ('Diff :' , diffchange )
    messenger.sendtext(diff_txt)

    if diffchange >= float(global_config_val['percent']) :
        rebalance = (((amount_asset * price_now)+bath_balance)/2) 
        signal_sell = rebalance - bath_balance
        print ('Sell :' , signal_sell ,'Bath')
        sell_fiat (signal_sell)
        last_price = check_order() 
        config.set('CONFIG', 'last_price', str(last_price))
        with open('config.ini', 'w') as f:
          config.write(f)     
        signal_sell_txt = ('Sell :' , signal_sell ,'Bath')
        messenger.sendtext(signal_sell_txt)

    elif diffchange <= (((0-float(global_config_val['percent'])*2)+float(global_config_val['percent']))):
        rebalance = (((amount_asset * price_now)+bath_balance)/2) 
        signal_buy = rebalance - bath_balance
        print ('Buy :' , signal_buy ,'Bath')
        buy (signal_buy)
        last_price = check_order() 
        config.set('CONFIG', 'last_price', str(last_price))
        with open('config.ini', 'w') as f:
          config.write(f)    
        signal_buy_txt = ('Buy :' , signal_buy ,'Bath')
        messenger.sendtext(signal_buy_txt)

        
    else :
        last_price = check_order() 
        config.set('CONFIG', 'last_price', str(last_price))
        with open('config.ini', 'w') as f:
            config.write(f)
        print (' Wait Next time ')
        messenger.sendtext(' Wait Next time ')
        

# temp = global_config_val['api_secret']
# bytes(temp, encoding='utf-8')
# print(bytes(temp, encoding='utf-8'))

## Start ##
## ต้องเพิ่มตัวเก็บค่า error #####
response = requests.post(API_HOST + '/api/market/balances', headers=header, data=json_encode(data))
balance = response.json()
showError = balance['error']  #แสดงค่า error ต้องเป็น 0 ถึงรันต่อได้
print('checking error :', showError)
CheckAPIBitkub()

# info balance 
asset_sym = global_config_val['trade_sym'].split('_')[1] #ใส่ใน config เปลี่ยนค่าได้
balance_All = balance['result'] #balance ทั้งหมดใน wallet
main_asset = float(balance_All[asset_sym]['available']) #balance ของ main asset 
# main_asset = 10000.00 Test 
bath_balance = float(balance_All['THB']['available'])
first_buy = bath_balance/2 # นำTHB ไปซื้อ asset ครึ่งหนึ่ง 
price_now = ticker(global_config_val['trade_sym'],'highestBid') #ตัวในช่องแรกควร Config ได้เพื่อเปลี่ยนคู่ Rebalnce
amount_asset = main_asset
last_price = check_order() 
# last_price = 0 Test 
config.set('CONFIG', 'last_price', str(last_price))
with open('config.ini', 'w') as f:
    config.write(f) 

# print(float(global_config_val['last_price']))

print("-------------------------------------------------------")
print ('Your Rebalance :',global_config_val['trade_sym'])
print ('Diff Rebalance :',global_config_val['percent']) 
print(f'{asset_sym} : {main_asset}')
print(f'THB  : {bath_balance}')

resulttradesym_txt = 'Your Rebalance :',global_config_val['trade_sym']
resultDiff_txt = 'Diff Rebalance :',global_config_val['percent']
resultAsset_txt = (f'{asset_sym} : {main_asset}')
resultBathbalance_txt = (f'THB  : {bath_balance}')
messenger.sendtext(f'\n{resulttradesym_txt}\n{resultDiff_txt}\n{resultAsset_txt}\n{resultBathbalance_txt}')

if main_asset == 0.0 :
    print(f'ต้องนำไปซื้อ {asset_sym} : {first_buy} THB')
    messenger.sendtext(f'ต้องนำไปซื้อ {asset_sym} : {first_buy} THB')
    buy(first_buy) #ยังไม่เอาขึ้นเพราะเดียวมันไปซื้อจริง
    # timer(global_config_val['time'])
else:
    print ("นับถอยหลัง 1 ชั่วโมง")
    messenger.sendtext("นับถอยหลัง 1 ชั่วโมง")
    last_price = check_order() 
    config.set('CONFIG', 'last_price', str(last_price))
    with open('config.ini', 'w') as f:
        config.write(f)
    # timer(global_config_val['time'])
    pass