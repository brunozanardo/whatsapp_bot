from flask import Blueprint

whatsapp_bp = Blueprint('whatsapp', __name__)


def classify_intent(message):
    """Classifica a intenção da mensagem"""
    message_lower = message.lower()
    
    # Saudações
    if any(word in message_lower for word in ['oi', 'olá', 'hello', 'bom dia', 'boa tarde', 'boa noite']):
        return 'saudacao'
    
    # Cardápio
