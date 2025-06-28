# main.py
import requests
from bs4 import BeautifulSoup
s = requests.Session()
SEARCH_URL = "https://www.net.city.nagoya.jp/cgi-bin/sp04002"  # リクエストを送るURL

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'Referer' : 'https://www.net.city.nagoya.jp/cgi-bin/sp04001' 
}



# サーバーに送信する検索条件データ

payload = {
    'syumoku': '021',
    'month': '07',
    'day': '15',    
    'joken': '1',
    'kyoyo1': '07',   # 時間帯のコード
    'kyoyo2': '00',
    'chiiki': '20',
    'vlinefield': '41696', 
    'tran_div': '',          # 値が空なので空文字列
    'system1': '-135090240',
    'system2': '0',
    'mae_riymd': '',
    'mae_cnt': '0',
    'mae_shcd': '',
    'mae_kyocd': '',
    'page': '0',
    'flg': '0',
    'button': '照会',
}

response = s.get("https://www.net.city.nagoya.jp/cgi-bin/sp04001")
response.encoding = 'shift_jis'


# 値取得
soup = BeautifulSoup(response.text, 'lxml')
vlinefield_value = soup.find('input', attrs={'name': 'vlinefield'})['value']
system1_value = soup.find('input', attrs={'name': 'system1'})['value']
syumokunm_value = soup.find('option', attrs={'value': payload['syumoku']}).text #.textで卓球という文字を取ってくる
chiikinm_value = soup.find('option', attrs={'value': payload['chiiki']}).text 
kyoyo1nm_value = soup.find('option', attrs={'value': payload['kyoyo1']}).text 
# kyoyo2nm_value = soup.find('option', attrs={'value': payload['kyoyo2']}).text 



# 上書き
payload['vlinefield'] = vlinefield_value
payload['system1'] = system1_value
payload['syumokunm'] = syumokunm_value
payload['chiikinm'] = chiikinm_value
payload['kyoyo1nm'] = kyoyo1nm_value
# payload['kyoyo2'] = kyoyo2nm_value

# print("---これから送信するpayloadの中身---")
# print(payload)

response = s.post(
 SEARCH_URL,
 data = payload,
 headers= HEADERS
 )
response.encoding = 'shift_jis'

# print(response.text)
soup = BeautifulSoup(response.text, 'lxml')

result = soup.find('td', attrs={'class' : 'ERRLABEL1'}).text.strip()

print(result)