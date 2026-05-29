import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Авторизация
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Настройки безопасности (отключаем лишние блокировки для стабильности)
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

# Используем самую актуальную и быструю модель
model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=safety_settings
)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.json
    user_text = req.get('request', {}).get('command', '').strip()
    is_new_session = req.get('session', {}).get('new', False)
    
    if is_new_session or not user_text:
        reply = "Привет! На связи Gemini. О чем вы хотите меня спросить?"
    else:
        try:
            # Запрос к Google
            response = model.generate_content(user_text)
            
            # Проверяем, есть ли вообще текст в ответе
            if response.text:
                reply = response.text
            else:
                reply = "Джеминай вернул пустой ответ. Попробуйте перефразировать вопрос."
        except Exception as e:
            # Выводим РЕАЛЬНУЮ причину в логи Render
            print(f"!!! REAL GEMINI ERROR: {str(e)}")
            reply = "Извините, произошла ошибка при обращении к Gemini. Попробуйте еще раз."

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
