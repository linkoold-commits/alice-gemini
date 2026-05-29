import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Получаем ваш ключ API из настроек Render
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.json
    user_text = req.get('request', {}).get('command', '').strip()
    is_new_session = req.get('session', {}).get('new', False)
    
    # Стартовая реплика при запуске
    if is_new_session or not user_text:
        return jsonify({
            "response": {
                "text": "Привет! На связи Джеминай. О чем вы хотите меня спросить?",
                "end_session": False
            },
            "version": "1.0"
        })
    
    # Альтернативное стабильное зеркало для работы с новыми ключами AQ.Ab8RN
    url = f"https://gateway.ai.cloudflare.com/v1/public/gemini-proxy/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
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
        # Отправляем POST запрос
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        
        # Проверяем структуру ответа
        if 'candidates' in res_data and res_data['candidates']:
            reply = res_data['candidates'][0]['content']['parts'][0]['text']
        elif 'error' in res_data:
            reply = f"Ошибка от Гугла: {res_data['error'].get('message', 'Пустое сообщение ошибки')}"
        else:
            reply = f"Неизвестный формат ответа. Статус ответа: {response.status_code}"
            
    except Exception as e:
        # Алиса сама скажет, почему Python споткнулся
        reply = f"Системный сбой кода: {str(e)}"
