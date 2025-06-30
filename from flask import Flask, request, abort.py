from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# ★★ここを自分のLINE Botの情報に書き換えてね！★★
LINE_CHANNEL_ACCESS_TOKEN = 'TvzgSYB73Tb0otdpzpoUaDk6qLpj+6vu5lPzztox5ZIQsLY5jz7d1Jcrb0g5bI1+fVUDVL1qqNQV+Nh2za6zCap94wqkUKmUqfT5K8p0WjAtluMDthZYlBTLOCmcimF4x5pDPwkFqLO/i702ey44/wdB04t89/1O/w1cDnyilFU='
LINE_CHANNEL_SECRET = '2dccf6a6608b8b28ec6f96b463a5fa17'

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

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
    msg = event.message.text
    reply = f"あなたはこう言いました：{msg}"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run(port=8000)