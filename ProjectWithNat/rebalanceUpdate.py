### for update my project ### 


import hashlib
import hmac
import json
import requests

# API info
API_HOST = 'https://api.bitkub.com'
API_KEY = '0f23ea15be12144c0a5d0a32f89d8402'
API_SECRET = b'6cf25bd3a3d5f390d328387a7174beb3'

def json_encode(data):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)

def sign(data):
    j = json_encode(data)
    #print('Signing payload: ' + j)
    h = hmac.new(API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
    return h.hexdigest()

# check server time
response = requests.get(API_HOST + '/api/servertime')
ts = int(response.text)
print('Server time: ' + response.text)

# check balances
header = {
'Accept': 'application/json',
'Content-Type': 'application/json',
'X-BTK-APIKEY': API_KEY,
}
data = {
    'ts': ts,
}
signature = sign(data)
data['sig'] = signature

print('Payload with signature: ' + json_encode(data))
response = requests.post(API_HOST + '/api/market/balances', headers=header, data=json_encode(data))
     #print('Balances: ' + response.text)
    #print(type(response))

##### ต้องเพิ่มตัวเก็บค่า error #####
balance = response.json()
showError = balance['error']  #แสดงค่า error ต้องเป็น 0 ถึงรันต่อได้
print('checking error :', showError)

def CheckAPIBitkub():

    if showError == 0 :  
        print("-------------------------------------------------------")
        print("--------------- Welcome to Rebalance BOT --------------")
        print("Bitkub API Checking : ok ")

    else:
        print("-------------------------------------------------------")
        print("Bitkub API Checking : Error!!!!! ")
        print("Please recheck your API . . . ")
        print("-------------------------------------------------------")

CheckAPIBitkub()

#def checkbalance in progress . . . . . . . . .
# info balance 
asset_sym = 'USDT' #ใส่ใน config เปลี่ยนค่าได้
balance_All = balance['result'] #balance ทั้งหมดใน wallet
main_asset = float(balance_All[asset_sym]['available']) #balance ของ main asset 
bath_balance = float(balance_All['THB']['available'])
first_buy = bath_balance/2 # นำTHB ไปซื้อ asset ครึ่งหนึ่ง 
#last_price = ['']
print("-------------------------------------------------------")
print(f'{asset_sym} : {main_asset}')
print(f'THB  : {bath_balance}')

if main_asset == 0.0 :
    print(f'ต้องนำไปซื้อ {asset_sym} : {first_buy} THB')
    #def buy(first_buy)
    

else:
    pass

'''
เช็คยอดเงินคงเหลือว่ามีเท่าไหร่ def check balance ,
    if  main_asset = 0 ให้ทำดังนี้
      bath_balance = เก็บค่า Balance Bath ออกมาด้วย หากยังให้ทำตามด้านล่าง
      เสร็จแล้วให้นำค่าออกมาแล้วหาร 2 ,
         first_buy(เงินส่วนที่ต้องนำไปซื้อ Bitcoin) = bath_balance/2
      นำครึ่งนึงไปซื้อ BTC ตามที่จำนวนมี ,
          def buy(first_buy)
      ให้ไปเก็บค่าใน Order history ออกมาไว้เพื่ออ้างอิงต่อไป ,
         last_price = def price_last_order ล่าสุด
         จบขั้นตอนแรกเป็นอันจบ

         bath_balance = balance บาทที่มี
         first_buy = จำนวนเงินรอบแรกที่ต้องนำไปซื้อ asset
         last_price = ราคาล่าสุดที่ซื้อ Bitcoin ไป
    else pass
'''