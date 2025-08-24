from flask import Blueprint, request, jsonify
import requests
import os
import json
from datetime import datetime

from utils.cardapio import (
    get_cardapio_completo,
    get_ingredientes,
    get_modo_preparo,
)


whatsapp_bp = Blueprint('whatsapp', __name__)


def classify_intent(message):
    """Classifica a intenção da mensagem"""
    message_lower = message.lower()
    
    # Saudações
    if any(word in message_lower for word in ['oi', 'olá', 'hello', 'bom dia', 'boa tarde', 'boa noite']):
        return 'saudacao'
    
    # Cardápio
