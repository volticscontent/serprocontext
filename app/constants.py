"""
Configurações CONSTANTES do Bot e-CAC
(Dados fixos que nunca mudam - configuração do sistema)
"""

# ==================== SERPRO CONSTANTES ====================
SERPRO_BASE_URL = "https://gateway.apiserpro.serpro.gov.br/integra-contador/v1"
SERPRO_TOKEN_URL = "https://gateway.apiserpro.serpro.gov.br/token"

# Suas credenciais fixas do SERPRO
SERPRO_CONSUMER_KEY = "fddUi1Ks7TjsQQ0skrT7jsA9Onoa"
SERPRO_CONSUMER_SECRET = "yA6nleyxTV_GlYkDg8xjyrAjh0Qa"
SERPRO_AMBIENTE = "homologacao"

# Seu certificado digital fixo
CERTIFICADO_PATH = "./certs/HAYLANDER MARTINS CONTABILIDADE LTDA51564549000140.pfx"
CERTIFICADO_SENHA = "300@Martins"
CPF_PROCURADOR = "122.643.046-50"

# ==================== DATABASE CONSTANTES ====================
DB_HOST = "161.35.141.62"
DB_PORT = 9000
DB_USER = "postgres"
DB_PASSWORD = "3ad3550763e84d5864a7"
DB_NAME = "n8n_usenodes"
DB_SCHEMA = "public"

# ==================== API CONSTANTES ====================
API_TITLE = "Bot e-CAC API"
API_DESCRIPTION = "API para consultas automatizadas no e-CAC via Integra Contador"
API_VERSION = "1.0.0"
API_PORT = 8000

# ==================== TIMEOUTS E LIMITES ====================
REQUEST_TIMEOUT_SECONDS = 30
TOKEN_CACHE_MINUTES = 55
MAX_RETRIES = 3
RATE_LIMIT_PER_MINUTE = 60

# ==================== MENSAGENS PADRÃO ====================
MENSAGENS_PADRAO = {
    "aguardando_cnpj": "CNPJ não identificado. Aguardando fornecimento pelo cliente.",
    "aguardando_razao_social": "Razão social não identificada. Aguardando fornecimento pelo cliente.",
    "aguardando_atendente": "Dados incompletos. Aguardando intervenção do atendente.",
    "consulta_sucesso": "Consulta realizada com sucesso.",
    "erro_serpro": "Erro ao consultar dados no SERPRO. Tente novamente.",
    "cnpj_invalido": "CNPJ inválido. Verifique o formato."
} 