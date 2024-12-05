from flask import Flask, render_template, request, jsonify
import os
import time
from datetime import datetime
import json
from time import sleep
import threading
from http.client import HTTPSConnection
from sys import stderr

app = Flask(__name__)

# Đọc nội dung từ file
def read_tokens_from_file(filename='token.txt'):
    with open(filename, 'r', encoding='utf-8') as file:
        tokens = file.readlines()
        return [token.strip() for token in tokens]

def read_content_from_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        return file.read().strip()

def get_connection():
    return HTTPSConnection("discordapp.com", 443)

def send_message(token, channel_id, message_data):
    header_data = {
        "content-type": "application/json",
        "user-agent": "discordapp.com",
        "authorization": token,
        "host": "discordapp.com",
    }
    conn = get_connection()
    try:
        conn.request("POST", f"/api/v9/channels/{channel_id}/messages", message_data, header_data)
        resp = conn.getresponse()
        if 199 < resp.status < 300:
            return True
        else:
            stderr.write(f"HTTP received {resp.status}: {resp.reason}\n")
            return False
    except Exception as e:
        stderr.write(f"Error: {str(e)}\n")
        return False

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        token = request.form['token']
        ci1 = request.form['channel_id']
        content_to_spam = request.form['content']
        cd = int(request.form['delay_time'])
        
        if not token or not ci1 or not content_to_spam or cd < 1:
            return render_template('index.html', error="Thông tin không hợp lệ. Vui lòng nhập đầy đủ!")
        
        # Bắt đầu một luồng riêng cho mỗi yêu cầu
        threading.Thread(target=send_spam_messages, args=([token], ci1, content_to_spam, cd)).start()
        return render_template('index.html', status="Spam process started")
    
    return render_template('index.html')

def send_spam_messages(tokens, ci1, content_to_spam, cd):
    message_data = json.dumps({
        "content": content_to_spam,
        "tts": "false",
    })
    count = 0
    while True:
        for token in tokens:
            success = send_message(token, ci1, message_data)
            if success:
                count += 1
            sleep(cd)
            if count % 10 == 0:
                print(f"Sent {count} messages")

if __name__ == '__main__':
    # Đảm bảo Flask chạy với multi-threading
    app.run(debug=True, threaded=True)

