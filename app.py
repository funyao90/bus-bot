from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import dateparser
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import threading
import bisect
import re

app = Flask(__name__)
task_list = []  # タスクを保存するリスト

# ★★ここを自分のLINE Botの情報に書き換えてね！★★
LINE_CHANNEL_ACCESS_TOKEN = 'TvzgSYB73Tb0otdpzpoUaDk6qLpj+6vu5lPzztox5ZIQsLY5jz7d1Jcrb0g5bI1+fVUDVL1qqNQV+Nh2za6zCap94wqkUKmUqfT5K8p0WjAtluMDthZYlBTLOCmcimF4x5pDPwkFqLO/i702ey44/wdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '2dccf6a6608b8b28ec6f96b463a5fa17'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

timetable = [825, 835, 845, 915, 925, 955, 1015, 1025, 1035, 1045, 1210, 1230, 1240, 1250, 1300, 1310, 1335, 1415, 1440, 1450, 1505, 1515, 1620, 1630, 1645, 1700, 1710, 1725, 1755, 1820, 1840, 1850, 1900, 1940, 2035, 2045, 2135]
timetable_sort = sorted(timetable)

timetable1 = [745, 755, 800, 802, 830, 835, 845, 855, 905, 915, 925, 933, 941, 945, 949, 953, 957, 1001, 1005, 1009, 1013, 1017, 1020, 1025, 1035, 1050, 1105, 1120, 1135, 1145, 1155, 1205, 1220, 1225, 1228, 1231, 1234, 1237, 1240, 1243, 1246, 1249, 1250, 1305, 1320, 1330, 1340, 1350, 1405, 1410, 1415, 1420, 1425, 1430, 1435, 1440, 1445, 1455, 1505, 1515, 1535, 1545, 1600, 1615, 1625, 1635, 1645, 1655, 1720, 1745, 1815, 1840, 1920, 1945, 2015, 2040, 2115]
timetable1_sort = sorted(timetable1)

timetable2 = [855, 900, 945, 1030, 1045, 1115, 1145, 1155, 1200, 1207, 1210, 1213, 1216, 1219, 1222, 1225, 1228, 1230, 1235, 1245, 1255, 1305, 1315, 1325, 1335, 1345, 1355, 1405, 1410, 1420, 1430, 1440, 1450, 1455, 1500, 1505, 1510, 1520, 1530, 1540, 1550, 1600, 1610, 1620, 1630, 1640, 1650, 1655, 1700, 1705, 1710, 1715, 1720, 1725, 1730, 1735, 1740, 1745, 1755, 1805, 1815, 1825, 1835, 1845, 1850, 1855, 1900, 1905, 1910, 1915, 1920, 1930, 1940, 1950, 1955, 2000, 2005, 2010, 2015, 2025, 2035, 2045, 2055, 2100, 2120, 2140]
timetable2_sort = sorted(timetable2)

timetable3 = [820, 830, 840, 910, 920, 950, 1010, 1020, 1030, 1040, 1205, 1225, 1235, 1245, 1255, 1305, 1330, 1410, 1420, 1445, 1500, 1510, 1615, 1625, 1640, 1655, 1705, 1720, 1750, 1810, 1835, 1845, 1855, 1905, 2030, 2040, 2100]
timetable3_sort = sorted(timetable3)
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_text = event.message.text
    user_id = event.source.user_id  # 誰が送ったか取得
    
    split_text = user_text.split(' ', 1)
    print(split_text[0])
    # バスの時間の処理
    if split_text[0] == "フロンティアリサーチセンター→所沢キャンパス":
        now = datetime.now()
        hhmm = now.strftime("%H%M")
        ans = bisect.bisect_left(timetable_sort, int(hhmm))
        reply = timetable_sort[ans]
    elif re.search(r"小手指→所沢キャンパス", split_text[0]):
        now = datetime.now()
        hhmm = now.strftime("%H%M")
        ans = bisect.bisect_left(timetable1_sort, int(hhmm))
        reply = timetable1_sort[ans]
    elif re.search(r"所沢キャンパス→小手指", split_text[0]):
        now = datetime.now()
        hhmm = now.strftime("%H%M")
        ans = bisect.bisect_left(timetable2_sort, int(hhmm))
        reply = timetable2_sort[ans]
    elif re.search(r"所沢キャンパス→フロンティアリサーチセンター", split_text[0]):
        now = datetime.now()
        hhmm = now.strftime("%H%M")
        ans = bisect.bisect_left(timetable3_sort, int(hhmm))
        reply = timetable3_sort[ans]
    # 予定登録
    elif len(split_text) < 2:
        reply = "予定は「明日10時 レポート提出」のように送ってね！"
    else:
        time_part = split_text[0]
        task_part = split_text[1]
        parsed_time = dateparser.parse(time_part, settings={'PREFER_DATES_FROM': 'future'})

        if parsed_time is None:
            reply = "日時がわかりませんでした。もう一度教えて！"
        else:
            task_list.append({
                'user_id': user_id,
                'time': parsed_time,
                'text': task_part
            })
            reply = f"✅ タスク登録！\n📅 {parsed_time.strftime('%Y-%m-%d %H:%M')} に\n📝「{task_part}」"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

def check_tasks():
    now = datetime.now()
    for task in task_list[:]:  # コピーをループして、削除も安全に
        if now >= task['time']:
            try:
                line_bot_api.push_message(
                    task['user_id'],
                    TextSendMessage(text=f"🔔 リマインド：{task['text']} の時間です！")
                )
                task_list.remove(task)  # 通知したら削除
            except Exception as e:
                print(f"通知エラー: {e}")



if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_tasks, 'interval', seconds=30)
    scheduler.start()

    # Flaskサーバーを別スレッドで起動
    flask_thread = threading.Thread(target=app.run, kwargs={"port": 8000})
    flask_thread.start()

    # メインスレッドをブロック（終了しないようにする）
    flask_thread.join()

