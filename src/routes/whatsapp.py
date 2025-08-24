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
