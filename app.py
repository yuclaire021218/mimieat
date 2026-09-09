from datetime import datetime
from flask import Flask, abort, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    FlexSendMessage,
    MessageEvent,
    TextMessage,
    TextSendMessage,
)
import pytz

app = Flask(__name__)

# 請換成你的 LINE Bot 憑證
line_bot_api = LineBotApi('L3Rcndneono0esFEeo7DvrXQGShmko3wS1GAc3gq+sqMCOhTnYHWX2270VRiNunfFM1UKaT5Ff0NAFYtamTuwZgTQvHw2j6+UNWxhfy+tdqBMUThQteICih3Lf4v+wYXEOowYhDim/E3FWxpwYr3VgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('9ed2121c3d710b6d44c6be9abe70d4fd')

feed_records = []
last_record_date = datetime.now(pytz.timezone('Asia/Taipei')).strftime(
    '%Y-%m-%d'
)


@app.route('/callback', methods=['POST'])
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
  global feed_records, last_record_date

  user_text = event.message.text.strip()

  tz = pytz.timezone('Asia/Taipei')
  now = datetime.now(tz)
  current_date = now.strftime('%Y-%m-%d')
  current_time = now.strftime('%H:%M')

  if current_date != last_record_date:
    feed_records = []
    last_record_date = current_date

  if user_text == '餵過咪米了':
    feed_records.append(current_time)
    records_str = '\n'.join([f'• 咪米已在 {t} 餵食過' for t in feed_records])

    flex_content = {
        'type': 'bubble',
        'body': {
            'type': 'box',
            'layout': 'vertical',
            'contents': [
                {
                    'type': 'text',
                    'text': '收到！🐾',
                    'weight': 'bold',
                    'size': 'md',
                    'color': '#1DB446',
                },
                {
                    'type': 'separator',
                    'margin': 'md',
                },
                {
                    'type': 'text',
                    'text': (
                        f'【今日咪米餵食紀錄】\n(更新時間: {current_time})\n\n'
                        + records_str
                    ),
                    'wrap': True,
                    'size': 'sm',
                    'color': '#555555',
                    'margin': 'md',
                },
            ],
        },
    }

    line_bot_api.reply_message(
        event.reply_token,
        FlexSendMessage(
            alt_text=f'收到！咪米已在 {current_time} 餵食過',
            contents=flex_content,
        ),
    )


import os

if __name__ == '__main__':
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)