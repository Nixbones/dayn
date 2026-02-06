from flask import Flask, request, jsonify
import hashlib
import requests
import os

app = Flask(__name__)

# --- НАСТРОЙКИ ---
TG_TOKEN = "7932064207:AAF5bvxFzjlPnmu053jEwlYWtDP7zQ1Wrac"
ADMIN_ID = "8161820784"
SECRET_SALT = "NixBones_Render_2026" 

# Список разрешенных HWID (добавляй сюда новые)
WHITELIST = [
    "7C1C98FC32FEAB8EEDDE92ACE8893C4DC342CBAC550548FCC37E417C8DF2F70C",
]

@app.route('/check', methods=['POST'])
def check():
    try:
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "No JSON data"}), 400
            
        # Убираем возможные пробелы по краям
        hwid = str(data.get("hwid", "")).strip()
        client_sig = str(data.get("sig", "")).strip()

        # Дебаг в логи сервера
        print(f"--- НОВЫЙ ЗАПРОС ---")
        print(f"ПОЛУЧЕН HWID: [{hwid}]")
        print(f"ПОЛУЧЕН SIG: [{client_sig}]")

        # Проверка подписи
        expected_sig = hashlib.sha256((hwid + SECRET_SALT).encode()).hexdigest()
        print(f"ОЖИДАЕМЫЙ SIG: [{expected_sig}]")
        
        if client_sig != expected_sig:
            print("РЕЗУЛЬТАТ: Ошибка подписи (SALT не совпадает?)")
            return jsonify({"status": "invalid_sig"}), 403

        if hwid in WHITELIST:
            print("РЕЗУЛЬТАТ: Доступ РАЗРЕШЕН")
            msg = f"🟢 <b>ДОСТУП РАЗРЕШЕН</b>\n🔑 HWID: <code>{hwid}</code>"
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          data={"chat_id": ADMIN_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
            return jsonify({"status": "granted"}), 200
        else:
            print(f"РЕЗУЛЬТАТ: HWID не найден в списке. В списке сейчас: {len(WHITELIST)} записей.")
            msg = f"🚨 <b>ОТКАЗ (Нет в списке)</b>\n🔑 HWID: <code>{hwid}</code>"
            requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", 
                          data={"chat_id": ADMIN_ID, "text": msg, "parse_mode": "HTML"}, timeout=5)
            return jsonify({"status": "denied"}), 403

    except Exception as e:
        print(f"КРИТИЧЕСКАЯ ОШИБКА: {e}")
        return jsonify({"status": "error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
