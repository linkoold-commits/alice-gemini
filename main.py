import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)

# Используем базовую стабильную модель
model = genai.GenerativeModel('gemini-pro')

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.json
    user_text = req.get('request', {}).get('command', '').strip()
    is_new_session = req.get('session', {}).get('new', False)
    
    if is_new_session or not user_text:
        reply = "Привет! На связи Gemini. О чем вы хотите меня спросить?"
    else:
        try:
            response = model.generate_content(user_text)
            reply = response.text
        except Exception as e:
            # Это покажет реальную ошибку в консоли Render
            print(f"!!! REAL GEMINI ERROR: {e}")
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
