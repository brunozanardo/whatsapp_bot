from flask import Blueprint, current_app, jsonify, request

whatsapp_bp = Blueprint('whatsapp', __name__)


def classify_intent(message):
    """Classifica a intenção da mensagem"""
    message_lower = message.lower()

    # Saudações
    if any(word in message_lower for word in ['oi', 'olá', 'hello', 'bom dia', 'boa tarde', 'boa noite']):
        return 'saudacao'

    # Cardápio


@whatsapp_bp.route('/whatsapp', methods=['POST'])
def whatsapp_webhook():
    """Recebe webhooks do WhatsApp."""
    data = request.get_json()
    if not data:
        current_app.logger.warning('Webhook recebeu payload vazio ou inválido')
        return jsonify({'error': 'invalid payload'}), 400

    entry = data.get('entry', [])
    if not entry:
        current_app.logger.warning('Payload sem entry: %s', data)
        return jsonify({'error': 'missing entry'}), 400

    if len(entry) == 0 or 'changes' not in entry[0]:
        current_app.logger.warning('Entry incompleto no payload: %s', entry)
        return jsonify({'error': 'incomplete entry'}), 400

    changes = entry[0].get('changes', [])
    if not changes:
        current_app.logger.warning('Entry sem changes: %s', entry[0])
        return jsonify({'error': 'missing changes'}), 400

    value = changes[0].get('value', {})
    messages = value.get('messages', [])
    if not messages:
        current_app.logger.warning('Payload sem messages: %s', value)
        return jsonify({'error': 'missing messages'}), 400

    current_app.logger.info('Mensagem recebida do WhatsApp: %s', messages[0])
    return jsonify({'status': 'received'}), 200
