# 🚀 Deploy WhatsApp BOT no Google Cloud Platform

Este guia te ajudará a fazer o deploy do seu BOT WhatsApp no Google Cloud Run.

## 📋 Pré-requisitos

1. **Conta Google Cloud Platform** com billing ativado
2. **gcloud CLI** instalado e configurado
3. **Docker** instalado (opcional, o Cloud Build fará isso)

## 🛠️ Passo a Passo

### 1. Configurar o Google Cloud

```bash
# Fazer login no Google Cloud
gcloud auth login

# Listar projetos disponíveis
gcloud projects list

# Criar um novo projeto (opcional)
gcloud projects create whatsapp-bot-projeto --name="WhatsApp Bot"

# Definir o projeto ativo
gcloud config set project SEU_PROJECT_ID

# Habilitar APIs necessárias
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### 2. Deploy no Cloud Run

#### Opção A: Deploy Direto (Recomendado)

```bash
# Navegar para o diretório do projeto
cd whatsapp-bot-gcp

# Deploy direto no Cloud Run
gcloud run deploy whatsapp-bot \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars FLASK_ENV=production
```

#### Opção B: Build Manual + Deploy

```bash
# Build da imagem Docker
gcloud builds submit --tag gcr.io/SEU_PROJECT_ID/whatsapp-bot

# Deploy no Cloud Run
gcloud run deploy whatsapp-bot \
  --image gcr.io/SEU_PROJECT_ID/whatsapp-bot \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --max-instances 10 \
  --set-env-vars FLASK_ENV=production
```

### 3. Configurar Variáveis de Ambiente (Opcional)

Se você for usar WAHA e Typebot, configure as variáveis:

```bash
gcloud run services update whatsapp-bot \
  --region us-central1 \
  --set-env-vars \
  TYPEBOT_VIEWER_URL=https://seu-typebot-viewer.com,\
  WAHA_URL=https://seu-waha.com,\
  TYPEBOT_ID=seu_typebot_id,\
  VERIFY_TOKEN=seu_token_secreto
```

### 4. Verificar o Deploy

```bash
# Obter URL do serviço
gcloud run services describe whatsapp-bot --region us-central1 --format 'value(status.url)'

# Testar o health check
curl https://SEU_URL/health
```

## 💰 Estimativa de Custos

### Cloud Run (Pay-per-use)
- **Primeiras 2 milhões de requisições/mês**: GRATUITAS
- **CPU**: $0.00002400 por vCPU-segundo
- **Memória**: $0.00000250 por GiB-segundo
- **Requisições**: $0.40 por milhão (após o limite gratuito)

### Exemplo de Uso Mensal:
- **1000 mensagens/dia** (30.000/mês)
- **Tempo médio de processamento**: 200ms
- **Custo estimado**: ~$0.50-2.00/mês

## 🔧 Comandos Úteis

```bash
# Ver logs em tempo real
gcloud run services logs tail whatsapp-bot --region us-central1

# Atualizar o serviço
gcloud run services update whatsapp-bot --region us-central1

# Deletar o serviço
gcloud run services delete whatsapp-bot --region us-central1

# Listar serviços
gcloud run services list
```

## 🌐 URLs Importantes

Após o deploy, você terá:
- **URL principal**: `https://whatsapp-bot-HASH-uc.a.run.app`
- **Health check**: `https://whatsapp-bot-HASH-uc.a.run.app/health`
- **Webhook WhatsApp**: `https://whatsapp-bot-HASH-uc.a.run.app/webhook/whatsapp`
- **Webhook WAHA**: `https://whatsapp-bot-HASH-uc.a.run.app/webhook/waha`

## 🔒 Segurança

- O serviço está configurado para aceitar requisições não autenticadas
- Para produção, considere adicionar autenticação
- Use HTTPS sempre (Cloud Run fornece automaticamente)

## 📊 Monitoramento

- **Logs**: Google Cloud Logging
- **Métricas**: Google Cloud Monitoring
- **Alertas**: Configure alertas para erros ou alta latência

## 🆘 Troubleshooting

### Erro de Build
```bash
# Ver logs do build
gcloud builds log BUILD_ID
```

### Erro de Deploy
```bash
# Ver logs do serviço
gcloud run services logs read whatsapp-bot --region us-central1
```

### Teste Local
```bash
# Testar localmente com Docker
docker build -t whatsapp-bot .
docker run -p 8080:8080 -e PORT=8080 whatsapp-bot
```

## 🎉 Próximos Passos

1. **Configurar domínio customizado** (opcional)
2. **Configurar WAHA** para WhatsApp
3. **Configurar Typebot** para fluxos visuais
4. **Monitorar performance** e custos
5. **Implementar CI/CD** com GitHub Actions

