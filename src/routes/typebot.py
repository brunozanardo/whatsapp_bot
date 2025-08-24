from flask import Blueprint, request, jsonify
import requests
import os
import json
from datetime import datetime
import pandas as pd

typebot_bp = Blueprint('typebot', __name__)

def get_cardapio_completo():
    """Retorna o cardápio completo"""
    try:
        df = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "cardapio_exemplo.csv"))
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
        df = pd.read_csv('cardapio_exemplo.csv')
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
        df = pd.read_csv('cardapio_exemplo.csv')
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

def send_to_typebot(session_id, message):
    """Envia mensagem para o Typebot"""
    try:
        typebot_url = os.environ.get('TYPEBOT_VIEWER_URL', 'http://localhost:3001')
        typebot_id = os.environ.get('TYPEBOT_ID', 'default')
        
        payload = {
            "message": message,
            "sessionId": session_id
        }
        
        response = requests.post(
            f"{typebot_url}/api/v1/typebots/{typebot_id}/startChat",
            json=payload,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
    except Exception as e:
        print(f"Erro ao enviar para Typebot: {str(e)}")
        return None

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

@typebot_bp.route('/webhook', methods=['POST'])
def typebot_webhook():
    """Webhook para receber dados do Typebot"""
    try:
        data = request.get_json()
        
        # Processar dados do Typebot
        session_id = data.get('sessionId', '')
        message = data.get('message', '')
        variables = data.get('variables', {})
        
        # Lógica de negócio baseada nas variáveis do Typebot
        if 'action' in variables:
            action = variables['action']
            
            if action == 'get_cardapio':
                response = get_cardapio_completo()
            elif action == 'get_ingredientes':
                prato = variables.get('prato', '')
                response = get_ingredientes(prato)
            elif action == 'get_modo_preparo':
                prato = variables.get('prato', '')
                response = get_modo_preparo(prato)
            else:
                response = "Ação não reconhecida."
        else:
            response = "Dados insuficientes para processar a solicitação."
        
        # Retornar resposta para o Typebot
        return jsonify({
            'status': 'success',
            'response': response,
            'sessionId': session_id
        }), 200
        
    except Exception as e:
        print(f"Erro no webhook Typebot: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@typebot_bp.route('/send-to-typebot', methods=['POST'])
def send_to_typebot_endpoint():
    """Endpoint para enviar mensagem para o Typebot"""
    try:
        data = request.get_json()
        session_id = data.get('sessionId', f"session_{datetime.now().timestamp()}")
        message = data.get('message', '')
        
        if not message:
            return jsonify({'status': 'error', 'message': 'Message required'}), 400
        
        # Enviar para Typebot
        typebot_response = send_to_typebot(session_id, message)
        
        if typebot_response:
            return jsonify({
                'status': 'success',
                'typebot_response': typebot_response,
                'sessionId': session_id
            }), 200
        else:
            # Fallback para lógica local se Typebot não responder
            from routes.whatsapp import process_message
            local_response = process_message(message)
            
            return jsonify({
                'status': 'success',
                'fallback_response': local_response,
                'sessionId': session_id,
                'note': 'Typebot unavailable, using local logic'
            }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@typebot_bp.route('/process-action', methods=['POST'])
def process_action():
    """Processa ações específicas do Typebot"""
    try:
        data = request.get_json()
        action = data.get('action', '')
        parameters = data.get('parameters', {})
        
        if action == 'cardapio':
            result = get_cardapio_completo()
        elif action == 'ingredientes':
            prato = parameters.get('prato', '')
            result = get_ingredientes(prato)
        elif action == 'modo_preparo':
            prato = parameters.get('prato', '')
            result = get_modo_preparo(prato)
        else:
            result = f"Ação '{action}' não reconhecida."
        
        return jsonify({
            'status': 'success',
            'result': result,
            'action': action,
            'parameters': parameters
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@typebot_bp.route('/health', methods=['GET'])
def typebot_health():
    """Health check para integração Typebot"""
    try:
        # Testar conexão com Typebot (se configurado)
        typebot_url = os.environ.get('TYPEBOT_VIEWER_URL')
        typebot_status = 'not_configured'
        
        if typebot_url:
            try:
                response = requests.get(f"{typebot_url}/health", timeout=5)
                typebot_status = 'online' if response.status_code == 200 else 'offline'
            except:
                typebot_status = 'offline'
        
        # Testar conexão com WAHA (se configurado)
        waha_url = os.environ.get('WAHA_URL')
        waha_status = 'not_configured'
        
        if waha_url:
            try:
                response = requests.get(f"{waha_url}/api/sessions", timeout=5)
                waha_status = 'online' if response.status_code == 200 else 'offline'
            except:
                waha_status = 'offline'
        
        return jsonify({
            'status': 'ok',
            'service': 'typebot-integration',
            'components': {
                'typebot': typebot_status,
                'waha': waha_status,
                'cardapio_csv': 'ok' if os.path.exists('cardapio_exemplo.csv') else 'missing'
            },
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@typebot_bp.route('/')
def typebot_info():
    """Informações sobre as rotas Typebot"""
    return jsonify({
        'service': 'Typebot Integration Routes',
        'endpoints': {
            'webhook': '/typebot/webhook',
            'send_to_typebot': '/typebot/send-to-typebot',
            'process_action': '/typebot/process-action',
            'health': '/typebot/health'
        },
        'environment': {
            'typebot_configured': bool(os.environ.get('TYPEBOT_VIEWER_URL')),
            'waha_configured': bool(os.environ.get('WAHA_URL')),
            'typebot_id_configured': bool(os.environ.get('TYPEBOT_ID'))
        }
    })

