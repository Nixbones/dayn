from flask import Flask, request, jsonify
import hashlib
import requests
import os

app = Flask(__name__)

# СЕКРЕТЫ
TG_TOKEN = "7932064207:AAF5bvxFzjlPnmu053jEwlYWtDP7zQ1Wrac"
ADMIN_ID = "8161820784"
SECRET_SALT = "NixBones_Render_2026" # Обязательно смени и там, и там

# Список разрешенных HWID
WHITELIST = [
    "ТВОЙ_HWID_КОТОРЫЙ_ВЫДАЕТ_БОТ",
]

@app.route('/check', methods=['POST'])
def check():
    try:
        data = request.json
        hwid = data.get("hwid")
        client_sig = data.get("sig")

        # Проверка подписи
        expected_sig = hashlib.sha256((hwid + SECRET_SALT).encode()).hexdigest()
        
        if client_sig != expected_sig:
            return jsonify({"status": "invalid_sig"}), 403

        if hwid in WHITELIST:
            msg = f"🟢 <b>ДОСТУП РАЗРЕШЕН</b>\n🔑 HWID: <code>{hwid}</code>"
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          data={"chat_id": ADMIN_ID, "text": msg, "parse_mode": "HTML"})
            return jsonify({"status": "granted"}), 200
        else:
            msg = f"🚨 <b>ОТКАЗ</b>\n🔑 HWID: <code>{hwid}</code>"
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          data={"chat_id": ADMIN_ID, "text": msg, "parse_mode": "HTML"})
            return jsonify({"status": "denied"}), 403
    except Exception as e:
        return jsonify({"status": "error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))