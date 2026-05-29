import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Забираем ваш ключ API из настроек Render
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
    
    # Прямой URL к API через стабильное зеркало для обхода блокировок
    url = f"https://generativelanguage.proxy.ustclug.org/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
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
        # Отправляем запрос напрямую
        response = requests.post(url, json=payload, timeout=10)
        res_data = response.json()
        
        # Вытаскиваем текст ответа из структуры Google API
        reply = res_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        # Ошибка выведется в логи Render, если что-то не так с ключом
        print(f"!!! CRITICAL ERROR: {str(e)}")
        if 'res_data' in locals():
            print(f"!!! API RESPONSE: {res_data}")
        reply = "Извините, произошла ошибка при обработке запроса нейросетью. Попробуйте еще раз."

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
