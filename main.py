# main.py
import requests
from bs4 import BeautifulSoup
import datetime
import json
def search_on_date(s,month, day): 
    
    SEARCH_URL = "https://www.net.city.nagoya.jp/cgi-bin/sp04002"  # リクエストを送るURL

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'Referer' : 'https://www.net.city.nagoya.jp/cgi-bin/sp04001' 
    }



    # サーバに送信する検索条件データ
    payload = {
        'syumoku': '021',
        'month': month,
        'day': day,
        'joken': '1',
        'kyoyo1': '07',
        'kyoyo2': '00',
        'chiiki': '20',
        'vlinefield': '41696', 
        'tran_div': '  ',          
        'system1': '-135090240',
        'system2': '0',
        'mae_riymd': '        ',  
        'mae_cnt': '0',
        'mae_shcd': '    ',        
        'mae_kyocd': '  ',         
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
    select_chiiki = soup.find('select', attrs={'name': 'chiiki'})
    chiikinm_value = select_chiiki.find('option', attrs={'value': payload['chiiki']}).text

    select_kyoyo1 = soup.find('select', attrs={'name': 'kyoyo1'})
    kyoyo1nm_value = select_kyoyo1.find('option', attrs={'value': payload['kyoyo1']}).text
    select_kyoyo2 = soup.find('select', attrs={'name': 'kyoyo2'})
    kyoyo2nm_value = select_kyoyo2.find('option', attrs={'value': payload['kyoyo2']}).text 



    # 上書き
    payload['vlinefield'] = vlinefield_value
    payload['system1'] = system1_value
    payload['syumokunm'] = syumokunm_value
    payload['chiikinm'] = chiikinm_value
    payload['kyoyo1nm'] = kyoyo1nm_value
    payload['kyoyo2nm'] = kyoyo2nm_value

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

    table = soup.find('table', attrs={'border' : '1'})
    # 04:西区, 03: 北区, 02: 東区, 06: 中区, 07: 昭和区, 05: 中村区
    target_area_names = ['西区', '北区', '東区', '中区', '昭和区', '中村区']
    available_slots = [] # 空のリストを用意
    if table:
        data_rows = table.find_all('tr') # trだけ取り出す

        # ループで1つずつ取り出す。(1行目以降)
        for row in data_rows[1:]:
            cells = row.find_all('td') # tdのみ抽出
            area_name = cells[1].text.strip() # 地域名取得してarea_nameに格納
            # 対象の地域名があった場合それを出力する
            if area_name in target_area_names:
                # 時間を取得する
                time_str = cells[4].text.strip()
                # convert_time_to_floatで１９：３０ -> 19.5といった表記に変換する
                start_time, end_time = convert_time_to_float(time_str)
                # 情報を辞書にまとめる
                slot_info = {
                    "地域": area_name,
                    "施設": cells[2].text.strip(),
                    "開始": start_time,
                    "終了": end_time
                }
                # 全体のリストに追加
                available_slots.append(slot_info)

                # print(cells[1].text.strip())
                # print(cells[2].text.strip())
                # print(cells[4].text.strip())
                # 辞書リストを返す
        return available_slots
# 時間の加工をする関数
def convert_time_to_float(time_str): 
    # ['１９：３０−２１：００', '夜間Ｂ）']のように分割して
    # 最初の要素(１９：３０−２１：００)を変数に格納する
    time_range_str = time_str.split('（')[0]
    # .replaceで原始的に大文字->小文字に変換する
    half_time_str = time_range_str.replace('１', '1').replace('２', '2').replace('３', '3').replace('４', '4').replace('５', '5').replace('６', '6').replace('７', '7').replace('８', '8').replace('９', '9').replace('−', '-').replace('０', '0').replace('：', ':')
    # "-"で分割して開始時間を取得
    start_float = parse_time_to_float(half_time_str.split('-')[0])
    end_float = parse_time_to_float(half_time_str.split('-')[1])
    return (start_float, end_float)
# 19:30 -> 19.5といった少数表記に変換する関数
def parse_time_to_float(hh_mm_str): # '19:30'のような文字列を受け取る
    parts = hh_mm_str.split(':')
    hour = int(parts[0])
    minute = int(parts[1])

    time_float = hour
    if minute == 30: 
        time_float += 0.5
    return time_float
    

# 呼び出し
now_datetime = datetime.datetime.today() # 現在日時取得
# 前回のファイルを読み込む（差分取得のため)
try: 
    with open('results.json', 'r', encoding='utf-8') as f:
        previous_results = json.load(f)
except FileNotFoundError:
    previous_results = [] # 初回は空のものを用意
s = requests.Session()
final_results = []



for i in range(6):
    
    target_date = now_datetime + datetime.timedelta(days=i)
    # 土日(5, 6)をスキップするため、4以下(平日)のみ取ってくる
    if target_date.weekday() <= 4:
        print('★'+target_date.strftime('%m')+'月'+target_date.strftime('%d') + '日の検索結果★')
        # その日の空き情報を取得
        daily_results = search_on_date(s, target_date.strftime('%m'), target_date.strftime('%d'))
        daily_facility_slots = {} # 日ごとにリセットする
        for slot in daily_results : # 結果があったときのみ処理
            facility_name = slot['施設']
            if facility_name not in daily_facility_slots: 
                # 初出の場合は新しいキーを作り新しいリストを作成
                daily_facility_slots[facility_name] = [slot]
            else:
                # 既出ならappendで追加する
                daily_facility_slots[facility_name].append(slot)
        
        for facility_name, slots in daily_facility_slots.items(): 
            slots.sort(key=lambda x: x['開始'])
            for slot in slots:
                duration = slot['終了'] - slot['開始']
                if duration >= 3 and slot['開始'] >= 18:
                # 発見！
                    print(f"発見！ {facility_name} {slot['開始']}時から{slot['終了']}時まで ({duration}時間)")
                    found_slot = {
                            "日付": target_date.strftime('%Y-%m-%d'),
                            "施設": facility_name,
                            "開始": slot['開始'],
                            "終了": slot['終了']
                    }
                    final_results.append(found_slot)
            for i in range(len(slots) - 1):
                # 今見ている時間枠
                current_slot = slots[i] 
                # 次の時間枠
                next_slot = slots[i+1]
                
                
                # もし、今の時間枠の「終了」と、次の時間枠の「開始」が同じなら...
                if current_slot['終了'] == next_slot['開始']:
                    # これは連続している！
                    
                    # 合体させた場合の開始時刻と終了時刻を計算
                    merged_start = current_slot['開始']
                    merged_end = next_slot['終了']
                    
                    # 合体させた時間を計算
                    duration = merged_end - merged_start
                    
                    
                    # もし、合計時間が3時間以上で、かつ開始が18時以降なら...
                    if duration >= 3 and merged_start >= 18:
                        print(f"発見！ {facility_name} {merged_start}時から{merged_end}時まで ({duration}時間)")
                        found_slot = {
                            "日付": target_date.strftime('%Y-%m-%d'),
                            "施設": facility_name,
                            "開始": merged_start,
                            "終了": merged_end
                        }
                        final_results.append(found_slot)

newly_found_slots = [] # 新しく発見されたスロットを入れるリスト
for current_slot in final_results:
    if current_slot not in previous_results:
        newly_found_slots.append(current_slot)
# 新しく空きがあった場合メッセージ表示
if newly_found_slots: 
    print("★新しい空き枠を発見しました★")
    print(json.dumps(newly_found_slots, indent=2, ensure_ascii=False))
else:
    print("新しい空き枠はありませんでした")

with open('results.json', 'w', encoding='utf-8') as f:
    json.dump(final_results, f, indent=2, ensure_ascii=False)

print("検索が完了し、結果をresults.jsonに保存しました。")

    # print(daily_facility_slots)