# 🚀 API BOT E-CAC - ESPECIFICAÇÃO SIMPLIFICADA

## VISÃO GERAL

API REST que recebe dados do cliente e retorna informações consultadas no Integra Contador (SERPRO).

---

## 📡 ENDPOINT PRINCIPAL

### **POST** `/consultar-cliente`

**URL:** `https://seu-dominio.com/api/v1/consultar-cliente`

**Content-Type:** `application/json`

**Headers:**
```http
Content-Type: application/json
Authorization: Bearer {seu_token_api} (opcional)
```

---

## 📝 ESTRUTURA DA REQUISIÇÃO

```json
{
  "nome": "João Silva",
  "telefone": "11999887766",
  "data_de_hoje": "2025-01-20",
  "cnpj": "12345678000195",
  "razao_social": "JOÃO SILVA 12345678901",
  "message": "Consulta de dados MEI"
}
```

### **Campos Obrigatórios:**
- ✅ `cnpj`: String (14 dígitos, sem formatação)
- ✅ `razao_social`: String

### **Campos Opcionais:**
- 📞 `nome`: String
- 📞 `telefone`: String  
- 📅 `data_de_hoje`: String (YYYY-MM-DD)
- 💬 `message`: String

---

## 📊 ESTRUTURA DA RESPOSTA

```json
{
  "success": true,
  "timestamp": "2025-01-20T14:30:00Z",
  "dados_cliente": {
    "cnpj": "12345678000195",
    "razao_social": "JOÃO SILVA 12345678901",
    "nome": "João Silva",
    "telefone": "11999887766"
  },
  "dados_consultados": {
    "mei": {
      "is_mei": true,
      "situacao": "ATIVO",
      "valor_total_guias_abertas": 245.40,
      "anos_declaracoes_pendentes": ["2023", "2024"],
      "ano_exclusao_mei": null,
      "ano_exclusao_simples": null
    },
    "cadastro": {
      "estado": "SP",
      "municipio": "São Paulo", 
      "atividade_principal": "Desenvolvimento de programas de computador sob encomenda",
      "email": "joao@exemplo.com"
    },
    "dividas": {
      "divida_ativa_uniao": 0.00,
      "divida_ativa_estado": 0.00,
      "divida_ativa_municipio": 0.00
    }
  }
}
```

---

## 🔍 MAPEAMENTO DOS DADOS

### **DADOS COLETADOS (fornecidos pelo cliente):**
- 📋 CNPJ
- 📋 Razão Social
- 📋 Nome do contato
- 📋 Telefone
- 📋 Data da consulta

### **DADOS CONSULTADOS (via Integra Contador):**

#### **📊 PGMEI (MEI):**
- ✅ **Valor total de guias em aberto** → `GET /pgmei/divida-ativa/{cnpj}`
- ✅ **Anos com declarações pendentes** → `GET /pgdasd/declaracoes/{cnpj}`
- ✅ **Situação MEI** → `GET /ccmei/situacao-cadastral/{cnpj}`

#### **📊 SIMPLES NACIONAL:**
- ✅ **Ano de exclusão do Simples** → `GET /pgdasd/declaracoes/{cnpj}`
- ✅ **Ano de exclusão do MEI** → `GET /ccmei/dados/{cnpj}`

#### **📊 DADOS CADASTRAIS:**
- ✅ **Estado** → Consulta cadastral RFB
- ✅ **Município** → Consulta cadastral RFB  
- ✅ **Atividade Principal** → Consulta cadastral RFB
- ✅ **E-mail** → Dados do cadastro

#### **💰 DÍVIDAS ATIVAS:**
- ✅ **União** → `GET /pgmei/divida-ativa/{cnpj}`
- ✅ **Estado** → Integração com APIs estaduais
- ✅ **Município** → Integração com APIs municipais

---

## ⚡ FLUXO DE PROCESSAMENTO

```mermaid
graph TD
    A[Cliente envia dados] --> B[Validar CNPJ]
    B --> C[Autenticar Integra Contador]
    C --> D[Consultar PGMEI]
    D --> E[Consultar PGDASD]
    E --> F[Consultar CCMEI]
    F --> G[Consultar Dívidas]
    G --> H[Consolidar Dados]
    H --> I[Retornar Resposta]
```

---

## 📋 CÓDIGOS DE RESPOSTA

| Código | Status | Descrição |
|--------|--------|-----------|
| **200** | ✅ Sucesso | Consulta realizada com sucesso |
| **400** | ❌ Bad Request | CNPJ inválido ou dados incorretos |
| **401** | 🔒 Unauthorized | Token de API inválido |
| **404** | 🔍 Not Found | CNPJ não encontrado |
| **422** | ⚠️ Unprocessable | Dados válidos mas sem informações |
| **500** | 💥 Server Error | Erro interno do servidor |
| **503** | 🚫 Service Unavailable | Integra Contador indisponível |

---

## 🔧 EXEMPLO DE USO

### **Requisição:**
```bash
curl -X POST https://seu-dominio.com/api/v1/consultar-cliente \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer seu_token" \
  -d '{
    "nome": "João Silva",
    "telefone": "11999887766", 
    "data_de_hoje": "2025-01-20",
    "cnpj": "12345678000195",
    "razao_social": "JOÃO SILVA 12345678901",
    "message": "Consulta de dados MEI"
  }'
```

### **Resposta de Sucesso:**
```json
{
  "success": true,
  "timestamp": "2025-01-20T14:30:00Z",
  "request_id": "req_123456789",
  "dados_cliente": {
    "cnpj": "12345678000195",
    "cnpj_formatado": "12.345.678/0001-95",
    "razao_social": "JOÃO SILVA 12345678901",
    "nome": "João Silva",
    "telefone": "11999887766"
  },
  "dados_consultados": {
    "mei": {
      "is_mei": true,
      "situacao": "ATIVO",
      "data_abertura": "2022-03-15",
      "valor_total_guias_abertas": 245.40,
      "anos_declaracoes_pendentes": ["2023", "2024"],
      "ano_exclusao_mei": null,
      "ano_exclusao_simples": null
    },
    "cadastro": {
      "estado": "SP",
      "municipio": "São Paulo",
      "cep": "01310-100", 
      "atividade_principal": {
        "codigo": "6201-5/00",
        "descricao": "Desenvolvimento de programas de computador sob encomenda"
      },
      "email": "joao@exemplo.com"
    },
    "dividas": {
      "divida_ativa_uniao": 0.00,
      "divida_ativa_estado": 0.00,
      "divida_ativa_municipio": 0.00,
      "total_dividas": 0.00
    },
    "declaracoes": {
      "simples_nacional": {
        "possui": true,
        "anos_pendentes": ["2024"]
      },
      "mei": {
        "possui": true,
        "anos_pendentes": ["2023", "2024"]
      }
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

### **Resposta de Erro:**
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CNPJ",
    "message": "CNPJ inválido ou não encontrado",
    "details": [
      "CNPJ deve ter 14 dígitos",
      "Verifique se o CNPJ está ativo"
    ]
  },
  "timestamp": "2025-01-20T14:30:00Z",
  "request_id": "req_123456789"
}
```

---

## 🔐 AUTENTICAÇÃO (OPCIONAL)

Se você quiser proteger a API:

```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📊 ENDPOINTS ADICIONAIS

### **GET** `/health`
Verifica se a API está funcionando:
```json
{
  "status": "healthy",
  "integra_contador": "connected",
  "timestamp": "2025-01-20T14:30:00Z"
}
```

### **GET** `/status/{cnpj}`
Consulta rápida do status:
```json
{
  "cnpj": "12345678000195",
  "is_mei": true,
  "situacao": "ATIVO",
  "tem_pendencias": true
}
```

---

## 🏗️ TECNOLOGIAS SUGERIDAS

### **Backend:**
- **Python**: FastAPI ou Flask
- **Node.js**: Express.js ou NestJS
- **Banco**: PostgreSQL + Redis

### **Deploy:**
- **Docker** + Docker Compose
- **Cloud**: AWS, Azure, GCP
- **Monitoramento**: Prometheus + Grafana

---

## 📝 PRÓXIMOS PASSOS

1. **Implementar endpoint** `/consultar-cliente`
2. **Integrar com Integra Contador** (OAuth2)
3. **Adicionar validações** de CNPJ
4. **Implementar cache** para otimização
5. **Configurar logs** e monitoramento
6. **Testes** e documentação

---

**🚀 Quer que eu implemente esta API agora?** 

Preciso apenas de:
- ✅ Consumer Key + Consumer Secret (Integra Contador)
- ✅ Linguagem preferida (Python/Node.js)
- ✅ Onde vai rodar (local/cloud) 