# 🤖 INTEGRAÇÃO N8N → BOT E-CAC API

## 📋 **RESUMO DA SEPARAÇÃO**

### **🔒 CONSTANTES (Fixas no código - `app/constants.py`)**
```python
# Estas são SUAS configurações fixas:
SERPRO_CONSUMER_KEY = "fddUi1Ks7TjsQQ0skrT7jsA9Onoa"
SERPRO_CONSUMER_SECRET = "yA6nleyxTV_GlYkDg8xjyrAjh0Qa"
CERTIFICADO_PATH = "./certs/HAYLANDER_CERTIFICADO.pfx"
CERTIFICADO_SENHA = "300@Martins"
CPF_PROCURADOR = "122.643.046-50"
```

### **🔄 VARIÁVEIS DINÂMICAS (Vindas do n8n)**
```json
{
  "nome": "{{ $json.user.name }}",
  "telefone": "{{ $json.user.number }}",
  "data_de_hoje": "{{ $json.date }}",
  "cnpj": "se indetificado!",
  "razao_social": "se indetificado!",
  "message": "aguardando atendente!"
}
```

---

## 🚀 **ENDPOINTS PARA N8N**

### **📍 Endpoint Principal:**
```
POST http://localhost:8000/api/v1/n8n/consultar
```

### **📍 Webhook Flexível:**
```
POST http://localhost:8000/api/v1/n8n/webhook
```

---

## 📊 **CENÁRIOS DE USO**

### **🔴 CENÁRIO 1: Dados Incompletos**

**Request do n8n:**
```json
{
  "nome": "João Silva",
  "telefone": "11999887766",
  "data_de_hoje": "2025-01-20",
  "cnpj": "se indetificado!",
  "razao_social": "se indetificado!",
  "message": "aguardando atendente!"
}
```

**Response da API:**
```json
{
  "success": false,
  "timestamp": "2025-01-20T14:30:00Z",
  "request_id": "req_123456789",
  "status": "DADOS_INCOMPLETOS",
  "message": "CNPJ e Razão Social não identificados. Necessário solicitar ao cliente.",
  "dados_faltantes": ["CNPJ", "Razão Social"],
  "dados_recebidos": {
    "nome": "João Silva",
    "telefone": "11999887766",
    "cnpj_recebido": "se indetificado!",
    "razao_social_recebida": "se indetificado!",
    "message": "aguardando atendente!"
  },
  "proximos_passos": [
    "Solicitar CNPJ do cliente",
    "Solicitar razão social da empresa"
  ]
}
```

### **✅ CENÁRIO 2: Dados Completos**

**Request do n8n:**
```json
{
  "nome": "João Silva",
  "telefone": "11999887766",
  "data_de_hoje": "2025-01-20",
  "cnpj": "49189181000135",
  "razao_social": "Gustavo Souza de Oliveira",
  "message": "dados completos"
}
```

**Response da API:**
```json
{
  "success": true,
  "timestamp": "2025-01-20T14:30:00Z",
  "request_id": "req_987654321",
  "dados_cliente": {
    "cnpj": "49189181000135",
    "cnpj_formatado": "49.189.181/0001-35",
    "razao_social": "Gustavo Souza de Oliveira",
    "nome": "João Silva",
    "telefone": "11999887766"
  },
  "dados_consultados": {
    "mei": {
      "is_mei": true,
      "situacao": "ATIVO",
      "valor_total_guias_abertas": 245.40,
      "anos_declaracoes_pendentes": ["2023", "2024"]
    },
    "cadastro": {
      "estado": "SP",
      "municipio": "São Paulo",
      "atividade_principal": {
        "codigo": "6201-5/00",
        "descricao": "Desenvolvimento de programas de computador sob encomenda"
      }
    },
    "dividas": {
      "divida_ativa_uniao": 245.40,
      "total_dividas": 245.40
    }
  },
  "resumo": {
    "status_geral": "PENDENCIAS",
    "total_devido": 245.40,
    "acoes_necessarias": [
      "Regularizar declarações MEI 2023 e 2024",
      "Quitar guias em aberto"
    ]
  }
}
```

---

## ⚙️ **CONFIGURAÇÃO NO N8N**

### **1. HTTP Request Node:**
```
Method: POST
URL: http://localhost:8000/api/v1/n8n/consultar
Headers: 
  Content-Type: application/json

Body:
{
  "nome": "{{ $json.user.name }}",
  "telefone": "{{ $json.user.number }}",
  "data_de_hoje": "{{ $json.date }}",
  "cnpj": "{{ $json.cnpj || 'se indetificado!' }}",
  "razao_social": "{{ $json.razao_social || 'se indetificado!' }}",
  "message": "{{ $json.message || 'aguardando atendente!' }}"
}
```

### **2. IF Node (Verificar Response):**
```javascript
// Condição para dados completos:
{{ $json.success === true }}

// Condição para dados incompletos:
{{ $json.success === false && $json.status === 'DADOS_INCOMPLETOS' }}
```

### **3. Switch Node (Próximas Ações):**
```javascript
// Rota 1: Sucesso - Mostrar resultado
if ($json.success === true) {
  return "mostrar_resultado";
}

// Rota 2: Dados incompletos - Solicitar mais dados
if ($json.dados_faltantes.includes("CNPJ")) {
  return "solicitar_cnpj";
}

if ($json.dados_faltantes.includes("Razão Social")) {
  return "solicitar_razao_social";
}
```

---

## 🔍 **DETECÇÃO INTELIGENTE**

A API detecta automaticamente quando os dados são **placeholders**:

### **❌ Placeholders Detectados:**
```
"se indetificado!"
"se identificado!" 
"nao identificado"
"não identificado"
"aguardando"
"pendente"
```

### **✅ Dados Válidos:**
```
"49189181000135" (CNPJ real)
"Gustavo Souza de Oliveira" (razão social real)
```

---

## 📱 **FLUXO WHATSAPP + N8N + API**

```
1. 📱 Cliente manda mensagem no WhatsApp
      ↓
2. 🤖 N8N recebe e analisa a mensagem
      ↓
3. 🔍 N8N tenta extrair CNPJ/Razão Social
      ↓
4. 📡 N8N faz POST para /api/v1/n8n/consultar
      ↓
5. 🧠 API verifica se dados estão completos
      ↓
6a. ✅ Completos → Consulta SERPRO → Retorna resultado
6b. ❌ Incompletos → Retorna "dados_faltantes"
      ↓
7. 🤖 N8N decide próxima ação baseado na response
      ↓
8. 📱 Envia mensagem apropriada no WhatsApp
```

---

## 🎯 **ENDPOINTS DE STATUS**

### **Status da Integração:**
```
GET http://localhost:8000/api/v1/n8n/status
```

### **Health Check Geral:**
```
GET http://localhost:8000/health
```

---

## 🔧 **EXEMPLO COMPLETO N8N**

```json
{
  "meta": {
    "instanceId": "n8n_workflow_bot_ecac"
  },
  "nodes": [
    {
      "name": "WhatsApp Trigger",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300],
      "parameters": {
        "httpMethod": "POST",
        "path": "whatsapp"
      }
    },
    {
      "name": "Consultar Bot eCac",
      "type": "n8n-nodes-base.httpRequest",
      "position": [450, 300],
      "parameters": {
        "method": "POST",
        "url": "http://localhost:8000/api/v1/n8n/consultar",
        "sendHeaders": true,
        "headerParameters": {
          "parameters": [
            {
              "name": "Content-Type",
              "value": "application/json"
            }
          ]
        },
        "sendBody": true,
        "bodyParameters": {
          "parameters": [
            {
              "name": "nome",
              "value": "={{ $json.user.name }}"
            },
            {
              "name": "telefone", 
              "value": "={{ $json.user.number }}"
            },
            {
              "name": "data_de_hoje",
              "value": "={{ $json.date }}"
            },
            {
              "name": "cnpj",
              "value": "={{ $json.cnpj || 'se indetificado!' }}"
            },
            {
              "name": "razao_social",
              "value": "={{ $json.razao_social || 'se indetificado!' }}"
            },
            {
              "name": "message",
              "value": "={{ $json.message || 'aguardando atendente!' }}"
            }
          ]
        }
      }
    }
  ]
}
```

---

**🎉 Pronto! Agora o n8n pode enviar dados dinâmicos e a API decide inteligentemente se consulta o SERPRO ou solicita mais dados!** 