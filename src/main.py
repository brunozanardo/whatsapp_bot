import os
from flask import Flask
from flask_cors import CORS
from routes.whatsapp import whatsapp_bp
from routes.typebot import typebot_bp

app = Flask(__name__)
CORS(app)  # Permitir CORS para integração

# Registrar blueprints
app.register_blueprint(whatsapp_bp, url_prefix='/webhook')
app.register_blueprint(typebot_bp, url_prefix='/typebot')

@app.route('/')
def home():
    return {
        'status': 'online',
        'service': 'WhatsApp Bot + Typebot',
        'version': '2.0',
        'platform': 'Google Cloud Run',
        'endpoints': {
            'health': '/health',
            'whatsapp_webhook': '/webhook/whatsapp',
            'waha_webhook': '/webhook/waha',
            'typebot_webhook': '/typebot/webhook',
            'send_to_typebot': '/typebot/send-to-typebot'
        }
    }, 200

@app.route('/health')
def health():
    return {
        'status': 'ok', 
        'service': 'whatsapp-bot-typebot',
        'platform': 'Google Cloud Run',
        'components': {
            'flask': 'ok',
            'whatsapp_routes': 'ok',
            'typebot_routes': 'ok'
        }
    }, 200

if __name__ == '__main__':
    # For local development
    port = int(os.environ.get('PORT', 8080))
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)
