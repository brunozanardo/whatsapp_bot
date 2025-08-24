from flask import Blueprint, request, jsonify
import requests
import os
import json
from datetime import datetime
import pandas as pd

whatsapp_bp = Blueprint('whatsapp', __name__)

def get_cardapio_completo():
    """Retorna o cardápio completo"""
    try:
        df = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "..", "..", "cardapio_exemplo.csv")
        )
        cardapio = "🍽️ *CARDÁPIO COMPLETO* 🍽️\n\n"
        
        for index, row in df.iterrows():
            cardapio += f"🔸 *{row['prato']}*\n"
            cardapio += f"📝 {row['descricao']}\n"
            cardapio += f"💰 R$ {str(row['preco'])}\n"
            cardapio += f"⏱️ {row['tempo_preparo']}\n"
            cardapio += f"🛒 {row['link_compra']}\n\n"
        
        return cardapio
    except Exception as e:
        return f"❌ Erro ao carregar cardápio: {str(e)}"

def get_ingredientes(prato_nome):
    """Retorna os ingredientes de um prato específico"""
    try:
        df = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "..", "..", "cardapio_exemplo.csv")
        )
        prato = df[df['prato'].str.contains(prato_nome, case=False, na=False)]
        
        if not prato.empty:
            ingredientes = prato.iloc[0]['ingredientes']
            resposta = f"🥘 *Ingredientes - {prato.iloc[0]['prato']}*\n\n"
            resposta += f"📋 {ingredientes}\n\n"
            
            # Verificar alérgenos
            if 'dendê' in ingredientes.lower():
                resposta += "⚠️ *ATENÇÃO:* Este prato contém dendê (alérgeno comum)\n"
            
            return resposta
        else:
            return f"❌ Prato '{prato_nome}' não encontrado no cardápio."
    except Exception as e:
        return f"❌ Erro ao buscar ingredientes: {str(e)}"

def get_modo_preparo(prato_nome):
    """Retorna o modo de preparo de um prato específico"""
    try:
        df = pd.read_csv(
            os.path.join(os.path.dirname(__file__), "..", "..", "cardapio_exemplo.csv")
        )
        prato = df[df['prato'].str.contains(prato_nome, case=False, na=False)]
        
        if not prato.empty:
            modo_preparo = prato.iloc[0]['modo_preparo']
            tempo = prato.iloc[0]['tempo_preparo']
            resposta = f"👨‍🍳 *Como preparar - {prato.iloc[0]['prato']}*\n\n"
            resposta += f"📝 {modo_preparo}\n"
            resposta += f"⏱️ Tempo: {tempo}\n\n"
            resposta += "💡 *Dica:* Siga as instruções com cuidado para o melhor resultado!"
            
            return resposta
        else:
            return f"❌ Prato '{prato_nome}' não encontrado no cardápio."
    except Exception as e:
        return f"❌ Erro ao buscar modo de preparo: {str(e)}"

def classify_intent(message):
    """Classifica a intenção da mensagem"""
    message_lower = message.lower()
    
    # Saudações
    if any(word in message_lower for word in ['oi', 'olá', 'hello', 'bom dia', 'boa tarde', 'boa noite']):
        return 'saudacao'
    
    # Cardápio
    if any(word in message_lower for word in ['cardápio', 'cardapio', 'menu', 'pratos', 'comidas']):
        return 'cardapio'
    
    # Ingredientes
    if any(word in message_lower for word in ['ingredientes', 'ingrediente', 'tem', 'contém', 'contem']):
        return 'ingredientes'
    
    # Modo de preparo
    if any(word in message_lower for word in ['como preparar', 'preparo', 'receita', 'fazer']):
        return 'modo_preparo'
    
    # Atendente humano
    if any(word in message_lower for word in ['atendente', 'humano', 'pessoa', 'falar com']):
        return 'atendente'
    
    return 'desconhecido'

def send_waha_message(phone, message):
    """Envia mensagem via WAHA"""
    try:
        waha_url = os.environ.get('WAHA_URL', 'http://localhost:3000')
        
        payload = {
            "chatId": f"{phone}@c.us",
            "text": message
        }
        
        response = requests.post(
            f"{waha_url}/api/sendText",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar mensagem WAHA: {str(e)}")
        return False

@whatsapp_bp.route('/whatsapp', methods=['GET', 'POST'])
def whatsapp_webhook():
    """Webhook principal do WhatsApp"""
    if request.method == 'GET':
        # Verificação do webhook
        verify_token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        if verify_token == os.environ.get('VERIFY_TOKEN', 'meu_token_secreto'):
            return challenge
        else:
            return 'Token inválido', 403
    
    elif request.method == 'POST':
        # Processar mensagem recebida
        try:
            data = request.get_json()
            
            # Extrair informações da mensagem
            if 'entry' in data and len(data['entry']) > 0:
                entry = data['entry'][0]
                if 'changes' in entry and len(entry['changes']) > 0:
                    change = entry['changes'][0]
                    if 'value' in change and 'messages' in change['value']:
                        messages = change['value']['messages']
                        
                        for message in messages:
                            phone = message['from']
                            text = message.get('text', {}).get('body', '')
                            
                            # Processar mensagem
                            response_text = process_message(text)
                            
                            # Enviar resposta
                            send_waha_message(phone, response_text)
            
            return jsonify({'status': 'success'}), 200
            
        except Exception as e:
            print(f"Erro no webhook WhatsApp: {str(e)}")
            return jsonify({'status': 'error', 'message': str(e)}), 500

@whatsapp_bp.route('/waha', methods=['POST'])
def waha_webhook():
    """Webhook para WAHA"""
    try:
        data = request.get_json()
        
        if data.get('event') == 'message' and data.get('payload', {}).get('body'):
            phone = data['payload']['from'].replace('@c.us', '')
            message = data['payload']['body']
            
            # Processar mensagem
            response_text = process_message(message)
            
            # Enviar resposta
            send_waha_message(phone, response_text)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        print(f"Erro no webhook WAHA: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@whatsapp_bp.route('/test', methods=['POST'])
def test_message():
    """Endpoint para testar mensagens"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        response_text = process_message(message)
        
        return jsonify({
            'input': message,
            'output': response_text,
            'intent': classify_intent(message)
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def process_message(message):
    """Processa a mensagem e retorna a resposta apropriada"""
    intent = classify_intent(message)
    
    if intent == 'saudacao':
        return """🤖 *Olá! Bem-vindo ao nosso atendimento!*

Sou seu assistente virtual especializado em culinária amazônica. Como posso te ajudar hoje?

📋 *Opções disponíveis:*
• Ver cardápio completo
• Consultar ingredientes de um prato
• Saber como preparar um prato
• Falar com atendente humano

Digite sua escolha ou faça uma pergunta! 😊"""

    elif intent == 'cardapio':
        return get_cardapio_completo()
    
    elif intent == 'ingredientes':
        # Tentar extrair nome do prato da mensagem
        for palavra in ['moqueca', 'tucumã', 'caldeirada', 'açaí']:
            if palavra in message.lower():
                return get_ingredientes(palavra)
        
        return """🥘 *Para consultar ingredientes, me diga o nome do prato!*

Exemplos:
• "Ingredientes da moqueca"
• "O que tem no tucumã?"
• "Ingredientes caldeirada"

Ou digite "cardápio" para ver todos os pratos disponíveis."""

    elif intent == 'modo_preparo':
        # Tentar extrair nome do prato da mensagem
        for palavra in ['moqueca', 'tucumã', 'caldeirada', 'açaí']:
            if palavra in message.lower():
                return get_modo_preparo(palavra)
        
        return """👨‍🍳 *Para saber como preparar, me diga o nome do prato!*

Exemplos:
• "Como preparar moqueca?"
• "Receita do tucumã"
• "Como fazer caldeirada?"

Ou digite "cardápio" para ver todos os pratos disponíveis."""

    elif intent == 'atendente':
        return """👥 *Transferindo para atendente humano...*

Em breve um de nossos atendentes entrará em contato com você.

⏰ Horário de atendimento: Segunda a Sexta, 8h às 18h
📞 WhatsApp: (92) 99999-9999
📧 Email: contato@exemplo.com

Enquanto isso, posso continuar te ajudando com informações sobre nossos pratos! 😊"""

    else:
        return """🤔 *Não entendi sua mensagem...*

Posso te ajudar com:
• 📋 Ver cardápio completo
• 🥘 Consultar ingredientes de pratos
• 👨‍🍳 Saber como preparar pratos
• 👥 Falar com atendente humano

Digite uma dessas opções ou faça uma pergunta mais específica! 😊"""

@whatsapp_bp.route('/')
def whatsapp_info():
    """Informações sobre as rotas WhatsApp"""
    return jsonify({
        'service': 'WhatsApp Routes',
        'endpoints': {
            'whatsapp_webhook': '/webhook/whatsapp',
            'waha_webhook': '/webhook/waha',
            'test': '/webhook/test'
        }
    })

@whatsapp_bp.route('/send-test', methods=['POST'])
def send_test_message():
    """Endpoint para enviar mensagem de teste via WAHA"""
    try:
        data = request.get_json()
        phone = data.get('phone', '')
        message = data.get('message', 'Mensagem de teste do BOT')
        
        if not phone:
            return jsonify({'status': 'error', 'message': 'Phone number required'}), 400
        
        success = send_waha_message(phone, message)
        
        return jsonify({
            'status': 'success' if success else 'error',
            'message_sent': success,
            'phone': phone,
            'message': message
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

