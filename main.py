import os
from flask import Flask, request, jsonify
import requests

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
    
    # ЧЕТКИЙ ОФИЦИАЛЬНЫЙ АДРЕС ПО ДОКУМЕНТАЦИИ GOOGLE
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_text}
                ]
            }
        ]
    }
    
    try:
        # Прямой запрос без сторонних шлюзов
        response = requests.post(url, json=payload, timeout=10)
        
        # Если статус ответа не 200 (ОК), Алиса скажет код ошибки
        if response.status_code != 200:
            return jsonify({
                "response": {
                    "text": f"Гугл вернул ошибку со статусом {response.status_code}.",
                    "end_session": False
                },
                "version": "1.0"
            })
            
        res_data = response.json()
        
        # Если сам Гугл прислал ошибку внутри JSON
        if 'error' in res_data:
            return jsonify({
                "response": {
                    "text": f"Гугл ругается: {res_data['error'].get('message', 'Ошибка')}",
                    "end_session": False
                },
                "version": "1.0"
            })
            
        # Всё прошло успешно — вытаскиваем ответ нейросети
        reply = res_data['candidates'][0]['content']['parts'][0]['text']
        
    except Exception as e:
        reply = f"Ошибка обработки: {str(e)}"

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
