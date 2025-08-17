# ========================================
# BOT E-CAC - INTEGRA CONTADOR
# Arquivo de configuração de ambiente
# ========================================

# ========================================
# INTEGRA CONTADOR - CREDENCIAIS SERPRO
# ========================================
# Obtidas no Portal SERPRO após contratação
SERPRO_CONSUMER_KEY=your_consumer_key_here
SERPRO_CONSUMER_SECRET=your_consumer_secret_here

# URLs da API Integra Contador
SERPRO_BASE_URL=https://gateway.apiserpro.serpro.gov.br/integra-contador/v1
SERPRO_TOKEN_URL=https://gateway.apiserpro.serpro.gov.br/token

# Ambiente (production/homologacao)
SERPRO_ENVIRONMENT=production

# ========================================
# CERTIFICADO DIGITAL E-CNPJ
# ========================================
# Caminho para o arquivo do certificado
CERTIFICATE_PATH=/path/to/certificate.p12
CERTIFICATE_PASSWORD=certificate_password

# CNPJ da empresa (para validação)
COMPANY_CNPJ=00.000.000/0001-00

# ========================================
# BANCO DE DADOS
# ========================================
# PostgreSQL (recomendado para produção)
DATABASE_URL=postgresql://username:password@localhost:5432/bot_ecac
DB_HOST=localhost
DB_PORT=5432
DB_NAME=bot_ecac
DB_USER=postgres
DB_PASSWORD=your_db_password

# SQLite (para desenvolvimento/testes)
# DATABASE_URL=sqlite:///./bot_ecac.db

# ========================================
# REDIS (CACHE E SESSÕES)
# ========================================
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=your_redis_password
REDIS_DB=0

# ========================================
# CONFIGURAÇÕES DO BOT
# ========================================
# Nome e versão
BOT_NAME=BotECAC
BOT_VERSION=1.0.0

# Timeout para requisições (em segundos)
REQUEST_TIMEOUT=30

# Intervalo para renovação de token (em minutos)
TOKEN_REFRESH_INTERVAL=45

# Rate limiting
MAX_REQUESTS_PER_MINUTE=60
MAX_CONCURRENT_REQUESTS=10

# ========================================
# LOGS E MONITORAMENTO
# ========================================
# Nível de log (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Caminho para arquivos de log
LOG_FILE_PATH=./logs/bot_ecac.log

# Rotação de logs (dias)
LOG_RETENTION_DAYS=30

# ========================================
# NOTIFICAÇÕES
# ========================================
# Email (SMTP)
EMAIL_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
SMTP_USE_TLS=true

# Destinatários padrão
ADMIN_EMAIL=admin@yourcompany.com
ALERT_EMAIL=alerts@yourcompany.com

# WhatsApp/Telegram (opcional)
WHATSAPP_ENABLED=false
WHATSAPP_API_TOKEN=your_whatsapp_token

TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# ========================================
# WEBHOOKS E INTEGRAÇÕES
# ========================================
# URL base para webhooks
WEBHOOK_BASE_URL=https://your-domain.com/webhooks

# Secret para validação de webhooks
WEBHOOK_SECRET=your_webhook_secret

# Integração com sistema externo
EXTERNAL_API_URL=https://your-system.com/api
EXTERNAL_API_KEY=your_external_api_key

# ========================================
# CONFIGURAÇÕES DE SEGURANÇA
# ========================================
# Chave secreta para JWT/sessões
SECRET_KEY=your_super_secret_key_here

# Criptografia de dados sensíveis
ENCRYPTION_KEY=your_encryption_key_32_bytes

# Timeout de sessão (em minutos)
SESSION_TIMEOUT=120

# ========================================
# CONFIGURAÇÕES ESPECÍFICAS DO E-CAC
# ========================================
# Intervalo de verificação do caixa postal (em minutos)
CAIXA_POSTAL_CHECK_INTERVAL=30

# Intervalo de verificação de parcelamentos (em horas)
PARCELAMENTOS_CHECK_INTERVAL=6

# Dias de antecedência para alertas de vencimento
VENCIMENTO_ALERT_DAYS=7

# ========================================
# PROCURAÇÕES E CLIENTES
# ========================================
# Diretório para armazenar procurações
PROCURACOES_DIR=./data/procuracoes

# Validação automática de procurações
AUTO_VALIDATE_PROCURACOES=true

# ========================================
# BACKUP E ARQUIVAMENTO
# ========================================
# Diretório para arquivos baixados
DOWNLOADS_DIR=./data/downloads

# Período de retenção de arquivos (em dias)
FILES_RETENTION_DAYS=90

# Backup automático
BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=24
BACKUP_DIR=./backups

# ========================================
# DESENVOLVIMENTO E DEBUG
# ========================================
# Modo debug
DEBUG=false

# Salvar requisições/respostas para debug
SAVE_HTTP_LOGS=false

# Diretório para logs de debug
DEBUG_DIR=./debug

# Mock de APIs (para testes)
MOCK_SERPRO_API=false

# ========================================
# DOCKER E CONTAINERS
# ========================================
# Porta da aplicação
PORT=8000

# Host da aplicação
HOST=0.0.0.0

# Workers para aplicação
WORKERS=4

# ========================================
# MONITORAMENTO E MÉTRICAS
# ========================================
# Prometheus metrics
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=8001

# Health check
HEALTH_CHECK_ENABLED=true
HEALTH_CHECK_ENDPOINT=/health

# Sentry (error tracking)
SENTRY_ENABLED=false
SENTRY_DSN=https://your-sentry-dsn

# ========================================
# CONFIGURAÇÕES AVANÇADAS
# ========================================
# Pool de conexões HTTP
HTTP_POOL_CONNECTIONS=20
HTTP_POOL_MAXSIZE=20

# Timeout de conexão
CONNECT_TIMEOUT=10

# Retry automático
AUTO_RETRY_ENABLED=true
MAX_RETRY_ATTEMPTS=3
RETRY_BACKOFF_FACTOR=2

# ========================================
# TIMEZONE E LOCALIZAÇÃO
# ========================================
TIMEZONE=America/Sao_Paulo
LOCALE=pt_BR.UTF-8

# ========================================
# EXEMPLO DE USO:
# ========================================
# 1. Copie este arquivo para .env
# 2. Substitua todos os valores com suas configurações reais
# 3. NUNCA commite o arquivo .env no git
# 4. Use o .env.example como referência para novos ambientes 