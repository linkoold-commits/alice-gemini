import os
from flask import Flask, request, jsonify
import google.generativeai as genai
from google.api_core import client_options

app = Flask(__name__)

# Берем ваш новый ключ (который AQ.Ab8RN...)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Настраиваем обход блокировки через официальное зеркало
options = client_options.ClientOptions(api_endpoint="https://generativelanguage.proxy.ustclug.org")
genai.configure(api_key=GEMINI_API_KEY, client_options=options)

# Подключаем модель
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.json
    user_text = req.get('request', {}).get('command', '').strip()
    is_new_session = req.get('session', {}).get('new', False)
    
    if is_new_session or not user_text:
        reply = "Привет! На связи Джеминай. О чем вы хотите меня спросить?"
    else:
        try:
            # Запрос к зеркалу Gemini
            response = model.generate_content(user_text)
            if response and response.text:
                reply = response.text
            else:
                reply = "Джеминай не смог сгенерировать ответ. Попробуйте еще раз."
        except Exception as e:
            print(f"!!! REAL GEMINI ERROR: {str(e)}")
            reply = "Произошла ошибка при обращении к Джеминай. Попробуйте повторить запрос."

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
