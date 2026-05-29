import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Берем API-ключ из настроек сервера (для безопасности)
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Используем быструю и актуальную модель
model = genai.GenerativeModel('gemini-1.5-flash')

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.json
    
    # Проверяем, есть ли текст от пользователя
    user_text = req.get('request', {}).get('command', '').strip()
    
    # Проверяем, это первый запуск навыка или продолжение диалога
    is_new_session = req.get('session', {}).get('new', False)
    
    if is_new_session or not user_text:
        reply = "Привет! На связи Gemini. О чем вы хотите меня спросить?"
    else:
        try:
            # Отправляем запрос в нейросеть Google
            response = model.generate_content(user_text)
            reply = response.text
        except Exception as e:
            reply = "Извините, произошла ошибка при обращении к Gemini. Попробуйте еще раз."
            print(f"Error: {e}")

    # Формируем правильный ответ для Алисы, чтобы она не закрывала сессию
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
