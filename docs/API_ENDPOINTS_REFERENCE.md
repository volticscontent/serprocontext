# API INTEGRA CONTADOR - REFERÊNCIA TÉCNICA DE ENDPOINTS

## ÍNDICE
1. [Autenticação](#autenticação)
2. [Endpoints por Categoria](#endpoints-por-categoria)
3. [Estruturas de Dados](#estruturas-de-dados)
4. [Códigos de Erro](#códigos-de-erro)
5. [Exemplos de Uso](#exemplos-de-uso)

---

## AUTENTICAÇÃO

### Obter Token OAuth2
```http
POST https://gateway.apiserpro.serpro.gov.br/token
Content-Type: application/x-www-form-urlencoded
Authorization: Basic {base64(consumer_key:consumer_secret)}

grant_type=client_credentials
```

**Resposta:**
```json
{
  "access_token": "eyJ4NXQiOiJOVGRtWmpia...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "default"
}
```

---

## ENDPOINTS POR CATEGORIA

### 📊 SIMPLES NACIONAL (PGDASD)

#### Consultar Declarações
```http
GET /pgdasd/declaracoes/{cnpj}
GET /pgdasd/declaracoes/{cnpj}?ano={ano}
```

**Parâmetros:**
- `cnpj` (string): CNPJ sem formatação (14 dígitos)
- `ano` (int, opcional): Ano específico

**Resposta:**
```json
{
  "success": true,
  "data": {
    "cnpj": "12345678000195",
    "declaracoes": [
      {
        "periodo": "2024-01",
        "situacao": "TRANSMITIDA",
        "data_transmissao": "2024-02-20T14:30:00Z",
        "recibo": "RF202400123456789",
        "valor_devido": 1250.50,
        "data_vencimento": "2024-02-20"
      }
    ]
  }
}
```

#### Consultar Última Declaração
```http
GET /pgdasd/ultima-declaracao/{cnpj}
```

#### Consultar Declaração Específica
```http
GET /pgdasd/declaracao/{cnpj}/{periodo}
```

**Exemplo:** `/pgdasd/declaracao/12345678000195/2024-01`

#### Consultar Extrato DAS
```http
GET /pgdasd/extrato-das/{cnpj}/{periodo}
```

#### Gerar DAS
```http
POST /pgdasd/gerar-das/{cnpj}/{periodo}
```

**Body:**
```json
{
  "incluir_multa": true,
  "incluir_juros": true,
  "data_vencimento": "2024-02-20"
}
```

#### Entregar Declaração
```http
POST /pgdasd/entregar-declaracao/{cnpj}
```

**Body:**
```json
{
  "periodo": "2024-01",
  "xml_declaracao": "base64_encoded_xml",
  "assinatura_digital": "base64_encoded_signature"
}
```

---

### 👤 MEI (PGMEI)

#### Consultar Dívida Ativa
```http
GET /pgmei/divida-ativa/{cnpj}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "cnpj": "12345678000195",
    "dividas": [
      {
        "numero_inscricao": "123456789",
        "periodo": "2023-12",
        "valor_principal": 81.60,
        "valor_multa": 16.32,
        "valor_juros": 5.40,
        "valor_total": 103.32,
        "situacao": "ATIVA"
      }
    ],
    "valor_total_dividas": 103.32
  }
}
```

#### Gerar DAS MEI (PDF)
```http
POST /pgmei/gerar-das-pdf/{cnpj}/{periodo}
```

#### Gerar DAS MEI (Código de Barras)
```http
POST /pgmei/gerar-das-codigobarras/{cnpj}/{periodo}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "codigo_barras": "03399999999999999999999999999999999999999999",
    "linha_digitavel": "03399.99999 99999.999999 99999.999999 9 99999999999999",
    "valor": 81.60,
    "vencimento": "2024-02-20"
  }
}
```

#### Atualizar Benefício MEI
```http
PUT /pgmei/atualizar-beneficio/{cnpj}
```

---

### 🏆 CCMEI (Certificado MEI)

#### Consultar Dados CCMEI
```http
GET /ccmei/dados/{cnpj}
```

#### Consultar Situação Cadastral
```http
GET /ccmei/situacao-cadastral/{cnpj}
```

#### Emitir CCMEI
```http
POST /ccmei/emitir/{cnpj}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "certificado_base64": "JVBERi0xLjQKJcfsj6...",
    "numero_certificado": "2024123456789",
    "data_emissao": "2024-01-15T10:30:00Z",
    "validade": "2024-12-31"
  }
}
```

---

### 📋 DCTFWEB

#### Consultar Recibo
```http
GET /dctfweb/recibo/{cnpj}/{periodo}
```

#### Consultar Declaração Completa
```http
GET /dctfweb/declaracao-completa/{cnpj}/{periodo}
```

#### Consultar XML
```http
GET /dctfweb/xml/{cnpj}/{periodo}
```

#### Consultar Apuração MIT
```http
GET /dctfweb/apuracao-mit/{cnpj}/{periodo}
```

#### Consultar Apurações MIT por Ano
```http
GET /dctfweb/apuracoes-mit/{cnpj}/{ano}
```

#### Gerar Guia de Declaração
```http
POST /dctfweb/gerar-guia/{cnpj}/{periodo}
```

#### Transmitir Declaração
```http
POST /dctfweb/transmitir-declaracao/{cnpj}
```

---

### 📧 CAIXA POSTAL

#### Listar Mensagens
```http
GET /caixa-postal/mensagens/{cnpj}
GET /caixa-postal/mensagens/{cnpj}?status=NAO_LIDA&limit=50&offset=0
```

**Parâmetros de Query:**
- `status`: LIDA, NAO_LIDA, TODAS
- `limit`: Número máximo de mensagens (padrão: 50)
- `offset`: Deslocamento para paginação

**Resposta:**
```json
{
  "success": true,
  "data": {
    "mensagens": [
      {
        "id": "MSG123456789",
        "assunto": "Intimação - Declaração em Atraso",
        "remetente": "Receita Federal",
        "data_envio": "2024-01-15T09:00:00Z",
        "status": "NAO_LIDA",
        "prioridade": "ALTA",
        "tem_anexo": true,
        "prazo_resposta": "2024-02-15"
      }
    ],
    "total": 15,
    "nao_lidas": 3
  }
}
```

#### Obter Detalhes de Mensagem
```http
GET /caixa-postal/mensagem/{cnpj}/{id_mensagem}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "id": "MSG123456789",
    "assunto": "Intimação - Declaração em Atraso",
    "conteudo": "Texto completo da mensagem...",
    "anexos": [
      {
        "nome": "intimacao_123.pdf",
        "tamanho": 245760,
        "url_download": "/downloads/anexo/456789"
      }
    ]
  }
}
```

#### Indicador de Novas Mensagens
```http
GET /caixa-postal/indicador-novas/{cnpj}
```

---

### 📄 PROCURAÇÕES

#### Obter Procurações
```http
GET /procuracoes/{cnpj}
```

**Resposta:**
```json
{
  "success": true,
  "data": {
    "procuracoes": [
      {
        "cpf_procurador": "12345678901",
        "nome_procurador": "João Silva",
        "servicos_autorizados": [
          "PGDASD_CONSULTA",
          "PGDASD_GERACAO_DAS",
          "CAIXA_POSTAL"
        ],
        "data_inicio": "2024-01-01",
        "data_fim": "2024-12-31",
        "ativa": true
      }
    ]
  }
}
```

---

### 💰 PARCELAMENTOS

#### PARCSN (Parcelamento Simples Nacional)
```http
GET /parcsn/pedidos/{cnpj}
GET /parcsn/parcelamento/{cnpj}/{numero}
GET /parcsn/detalhes-pagamento/{cnpj}/{numero}/{parcela}
GET /parcsn/parcelas-impressao/{cnpj}/{numero}
POST /parcsn/emitir-documento/{cnpj}/{numero}/{parcela}
```

#### PARCMEI (Parcelamento MEI)
```http
GET /parcmei/pedidos/{cnpj}
GET /parcmei/parcelamento/{cnpj}/{numero}
GET /parcmei/detalhes-pagamento/{cnpj}/{numero}/{parcela}
GET /parcmei/parcelas-impressao/{cnpj}/{numero}
POST /parcmei/emitir-documento/{cnpj}/{numero}/{parcela}
```

#### Outros Tipos
- `PERTSN` - Perdão de Tributos Simples Nacional
- `RELPSN` - Religação Simples Nacional  
- `PERTMEI` - Perdão MEI
- `RELPMEI` - Religação MEI
- `PARCSN_ESPECIAL` - Parcelamento Especial SN
- `PARCMEI_ESPECIAL` - Parcelamento Especial MEI

**Resposta Parcelamento:**
```json
{
  "success": true,
  "data": {
    "numero_parcelamento": "2024000123456",
    "situacao": "ATIVO",
    "valor_total": 5000.00,
    "parcelas": [
      {
        "numero": 1,
        "valor": 500.00,
        "vencimento": "2024-02-15",
        "situacao": "PAGO",
        "data_pagamento": "2024-02-14"
      },
      {
        "numero": 2,
        "valor": 500.00,
        "vencimento": "2024-03-15",
        "situacao": "PENDENTE"
      }
    ]
  }
}
```

---

### 💳 PAGAMENTOS

#### Consultar Documento de Arrecadação Pago
```http
GET /pagamento/documento-arrecadacao/{cnpj}/{numero}
```

#### Gerar Comprovante de Pagamento
```http
POST /pagamento/gerar-comprovante/{cnpj}/{numero}
```

---

### 📊 SITUAÇÃO FISCAL (SITFIS)

#### Solicitar Relatório
```http
POST /sitfis/solicitar-relatorio/{cnpj}
```

#### Emitir Relatório
```http
GET /sitfis/emitir-relatorio/{cnpj}/{protocolo}
```

---

### 📑 SICALC/DARF

#### Consolidar e Emitir DARF
```http
POST /sicalc/consolidar-emitir-darf/{cnpj}/{periodo}
```

---

### 📄 DEFIS

#### Transmitir Declaração
```http
POST /defis/transmitir-declaracao/{cnpj}
```

---

### 📨 DTE (Documento de Transferência Eletrônica)

#### Obter Indicador
```http
GET /dte/indicador/{cnpj}
```

---

## ESTRUTURAS DE DADOS

### Headers Padrão
```http
Authorization: Bearer {access_token}
Content-Type: application/json
User-Agent: BotECAC/1.0
X-Request-ID: {uuid}
```

### Resposta Padrão de Sucesso
```json
{
  "success": true,
  "data": {},
  "message": "Operação realizada com sucesso",
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Resposta Padrão de Erro
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CNPJ",
    "message": "CNPJ inválido ou não encontrado",
    "details": [
      "O CNPJ deve ter 14 dígitos",
      "Verifique se o CNPJ está ativo na Receita Federal"
    ]
  },
  "timestamp": "2024-01-15T10:30:00Z",
  "request_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Tipos de Data
```json
{
  "periodo": "YYYY-MM",
  "data": "YYYY-MM-DD",
  "data_hora": "YYYY-MM-DDTHH:mm:ssZ",
  "cnpj": "12345678000195",
  "cpf": "12345678901"
}
```

---

## CÓDIGOS DE ERRO

### Autenticação
- `401001`: Token inválido ou expirado
- `401002`: Consumer Key/Secret inválidos
- `401003`: Certificado digital inválido

### Autorização
- `403001`: Sem procuração para o serviço
- `403002`: Procuração expirada
- `403003`: Serviço não autorizado na procuração

### Validação
- `400001`: CNPJ inválido
- `400002`: Período inválido
- `400003`: Parâmetros obrigatórios ausentes

### Negócio
- `422001`: Declaração não encontrada
- `422002`: Período não disponível para consulta
- `422003`: Parcelamento não localizado

### Sistema
- `500001`: Erro interno do servidor
- `500002`: Serviço temporariamente indisponível
- `500003`: Timeout na requisição

---

## EXEMPLOS DE USO

### Fluxo Completo - Consulta Simples Nacional

```python
import requests
import base64

# 1. Autenticação
consumer_key = "sua_consumer_key"
consumer_secret = "sua_consumer_secret"
credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

token_response = requests.post(
    "https://gateway.apiserpro.serpro.gov.br/token",
    headers={
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    },
    data="grant_type=client_credentials"
)

token = token_response.json()["access_token"]

# 2. Consultar declarações
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

cnpj = "12345678000195"
declaracoes_response = requests.get(
    f"https://gateway.apiserpro.serpro.gov.br/integra-contador/v1/pgdasd/declaracoes/{cnpj}",
    headers=headers
)

declaracoes = declaracoes_response.json()

# 3. Verificar caixa postal
caixa_response = requests.get(
    f"https://gateway.apiserpro.serpro.gov.br/integra-contador/v1/caixa-postal/mensagens/{cnpj}",
    headers=headers
)

mensagens = caixa_response.json()

# 4. Gerar DAS se necessário
if declaracoes["data"]["declaracoes"]:
    ultima_declaracao = declaracoes["data"]["declaracoes"][0]
    periodo = ultima_declaracao["periodo"]
    
    das_response = requests.post(
        f"https://gateway.apiserpro.serpro.gov.br/integra-contador/v1/pgdasd/gerar-das/{cnpj}/{periodo}",
        headers=headers,
        json={
            "incluir_multa": True,
            "incluir_juros": True
        }
    )
    
    das = das_response.json()
```

### Monitoramento Automático
```python
import asyncio
import aiohttp
from datetime import datetime, timedelta

class IntegradorECAC:
    def __init__(self, consumer_key, consumer_secret):
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = None
        self.token_expires = None
    
    async def get_token(self):
        if self.token and self.token_expires > datetime.now():
            return self.token
        
        # Renovar token
        credentials = base64.b64encode(
            f"{self.consumer_key}:{self.consumer_secret}".encode()
        ).decode()
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://gateway.apiserpro.serpro.gov.br/token",
                headers={
                    "Authorization": f"Basic {credentials}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data="grant_type=client_credentials"
            ) as response:
                data = await response.json()
                self.token = data["access_token"]
                self.token_expires = datetime.now() + timedelta(seconds=data["expires_in"] - 60)
                return self.token
    
    async def verificar_caixa_postal(self, cnpj):
        token = await self.get_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://gateway.apiserpro.serpro.gov.br/integra-contador/v1/caixa-postal/indicador-novas/{cnpj}",
                headers=headers
            ) as response:
                return await response.json()
    
    async def monitorar_clientes(self, cnpjs):
        while True:
            for cnpj in cnpjs:
                try:
                    resultado = await self.verificar_caixa_postal(cnpj)
                    if resultado["data"]["novas_mensagens"] > 0:
                        await self.processar_mensagens(cnpj)
                except Exception as e:
                    print(f"Erro ao verificar {cnpj}: {e}")
            
            await asyncio.sleep(1800)  # 30 minutos
```

### Rate Limiting e Retry
```python
import time
from functools import wraps

def rate_limit_retry(max_retries=3, backoff_factor=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    response = func(*args, **kwargs)
                    
                    if response.status_code == 429:  # Rate limited
                        wait_time = backoff_factor ** attempt
                        time.sleep(wait_time)
                        continue
                    
                    return response
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(backoff_factor ** attempt)
            
            return None
        return wrapper
    return decorator

@rate_limit_retry()
def consultar_api(url, headers):
    return requests.get(url, headers=headers)
```

---

**Versão**: 1.0  
**Última Atualização**: Janeiro 2025  
**Base URL**: `https://gateway.apiserpro.serpro.gov.br/integra-contador/v1` 