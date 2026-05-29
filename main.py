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
    
    # Стабильное зеркало от ИИ-сообщества, которое понимает новые ключи AQ.
    url = f"https://api.vllm-proxy.org/v1/chat/completions"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {GEMINI_API_KEY}"
    }
    
    payload = {
        "model": "gemini-1.5-flash",
        "messages": [
            {"role": "user", "content": user_text}
        ]
    }
    
    try:
        # Отправляем запрос через универсальный шлюз
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        res_data = response.json()
        
        # Если шлюз вернул ошибку
        if response.status_code != 200:
            error_msg = res_data.get('error', {}).get('message', 'Неизвестный сбой шлюза')
            return jsonify({
                "response": {
                    "text": f"Ошибка шлюза (Код {response.status_code}): {error_msg}",
                    "end_session": False
                },
                "version": "1.0"
            })
            
        # Забираем текст ответа (в формате OpenAI/vLLM шлюзов)
        reply = res_data['choices'][0]['message']['content']
        
    except Exception as e:
        reply = f"Ошибка связи с зеркалом: {str(e)}"

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
