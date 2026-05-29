import os
from flask import Flask, request, jsonify
import requests

# Отключаем предупреждения об отсутствии SSL-сертификата при запросе по IP
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)

# Ваш ключ API из настроек Render (AQ.Ab8RN...)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.json
    user_text = req.get('request', {}).get('command', '').strip()
    is_new_session = req.get('session', {}).get('new', False)
    
    # Стартовый диалог
    if is_new_session or not user_text:
        return jsonify({
            "response": {
                "text": "Привет! На связи Джеминай. О чем вы хотите меня спросить?",
                "end_session": False
            },
            "version": "1.0"
        })
    
    # СТУЧИМСЯ СТРОГО ПО ЦИФРОВОМУ IP (Шлюз Cloudflare)
    # Это полностью обходит ошибку "Name or service not known"
    url = "https://104.21.31.181/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Host": "api.chathub.gg" # Говорим шлюзу, куда на самом деле шел запрос
    }
    
    payload = {
        "model": "gemini-1.5-flash",
        "messages": [
            {"role": "user", "content": user_text}
        ]
    }
    
    try:
        # Отправляем запрос по IP, отключая проверку SSL (verify=False), так как домена нет
        response = requests.post(url, json=payload, headers=headers, verify=False, timeout=12)
        
        if response.status_code != 200:
            return jsonify({
                "response": {
                    "text": f"Шлюз принял запрос, но вернул ошибку {response.status_code}.",
                    "end_session": False
                },
                "version": "1.0"
            })
            
        res_data = response.json()
        reply = res_data['choices'][0]['message']['content']
        
    except Exception as e:
        reply = f"Прямой шлюз тоже заблокирован. Код сбоя: {str(e)}"

    return jsonify({
        "response": {
            "text": reply,
            "end_session": False
        },
        "version": "1.0"
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
