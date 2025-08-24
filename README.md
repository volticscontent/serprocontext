# 🤖 Bot e-CAC - Consultas SERPRO Integra Contador

**Sistema simples para consultas automatizadas via SERPRO Integra Contador**

## 🎯 **Objetivo**

Aplicação simples para consultar dados fiscais de clientes MEI através das APIs do SERPRO Integra Contador e armazenar na tabela `haylander` para análise contábil.

**FOCO**: Apenas **CONSULTAS** - sem emissão, sem geração de documentos.

## 🏗️ **Stack Simplificada**

### **Backend**
- **FastAPI** - Framework web leve e rápido
- **SQLAlchemy** - ORM simples
- **Pydantic** - Validação de dados
- **httpx** - Cliente HTTP assíncrono
- **loguru** - Logging simples

### **Cache Token** 
- **SQLite em memória** - Cache simples para tokens OAuth (sem Redis)
- **Arquivo local** - Fallback para persistência

### **Banco de Dados** 
- **SQLite** - Desenvolvimento e produção (simples)
- **PostgreSQL** - Opcional para produção

## 📊 **APIs SERPRO Consultadas**

Baseado na análise dos projetos GitHub, estas são as APIs **realmente consultáveis**:

### **APIs Disponíveis no Integra Contador:**
- ✅ `/pgmei/divida-ativa/{cnpj}` - **Dívidas ativas MEI**
- ✅ `/pgdasd/declaracoes/{cnpj}` - **Declarações PGDASD**  
- ✅ `/ccmei/dados/{cnpj}` - **Dados CCMEI**
- ✅ `/ccmei/situacao-cadastral/{cnpj}` - **Situação cadastral CCMEI**
- ✅ `/caixa-postal/mensagens/{cnpj}` - **Mensagens caixa postal**
- ✅ `/procuracoes/{cnpj}` - **Procurações ativas**

### **APIs Questionáveis (verificar se existem):**
- ❓ `/parcmei/pedidos/{cnpj}` - Parcelamentos MEI
- ❓ `/parcsn/pedidos/{cnpj}` - Parcelamentos Simples Nacional

## 📋 **Tabela Haylander (Simplificada para Consultas)**

```sql
CREATE TABLE haylander (
    -- Identificação
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cnpj VARCHAR(14) UNIQUE NOT NULL,
    razao_social VARCHAR(255),
    
    -- PGMEI - Dívida Ativa
    pgmei_divida_valor DECIMAL(15,2) DEFAULT 0.00,
    pgmei_tem_divida BOOLEAN DEFAULT FALSE,
    pgmei_ultimo_update TIMESTAMP,
    
    -- PGDASD - Declarações 
    pgdasd_pendentes_count INTEGER DEFAULT 0,
    pgdasd_anos_pendentes TEXT, -- "2022,2023,2024"
    pgdasd_ultimo_update TIMESTAMP,
    
    -- CCMEI - Dados Cadastrais
    ccmei_situacao VARCHAR(100),
    ccmei_data_abertura DATE,
    ccmei_ultimo_update TIMESTAMP,
    
    -- Caixa Postal
    caixa_mensagens_count INTEGER DEFAULT 0,
    caixa_mensagens_nao_lidas INTEGER DEFAULT 0,
    caixa_ultimo_update TIMESTAMP,
    
    -- Procurações
    procuracoes_ativas INTEGER DEFAULT 0,
    procuracoes_ultimo_update TIMESTAMP,
    
    -- Consolidação Simples
    situacao_geral VARCHAR(50), -- "OK", "PENDENCIAS", "PROBLEMAS"
    valor_total_pendente DECIMAL(15,2) DEFAULT 0.00,
    ultima_consulta TIMESTAMP,
    status_consulta VARCHAR(20), -- "SUCCESS", "ERROR"
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 **Estrutura Simplificada**

```
bot_ecac/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app principal
│   ├── config.py            # Configurações
│   ├── database.py          # SQLite connection
│   ├── models.py            # Modelo SQLAlchemy (tudo em um arquivo)
│   ├── schemas.py           # Pydantic schemas (tudo em um arquivo)
│   ├── serpro_client.py     # Cliente SERPRO simplificado
│   ├── token_cache.py       # Cache simples de token (sem Redis)
│   └── utils.py             # Utilitários
├── certs/                   # Certificados (mantido)
├── requirements.txt         # Dependências mínimas
├── .env.example             # Exemplo variáveis
├── alembic.ini              # Config migrações básicas
└── README.md
```

## 📦 **Dependências Mínimas**

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
httpx==0.25.2
loguru==0.7.2
python-dotenv==1.0.0
alembic==1.13.0
```

## ⚡ **Como Usar**

```bash
# 1. Instalar
pip install -r requirements.txt

# 2. Configurar
cp .env.example .env
# Editar com credenciais SERPRO

# 3. Inicializar banco
python -c "from app.database import init_db; init_db()"

# 4. Rodar
uvicorn app.main:app --reload --port 8000
```

## 📋 **APIs Simples**

### **Consultar Cliente**
```bash
POST /consultar/{cnpj}
# Consulta TODAS as APIs e atualiza tabela haylander
```

### **Ver Dados**
```bash
GET /cliente/{cnpj}
# Retorna dados consolidados da tabela
```

### **Listar Clientes**
```bash
GET /clientes
# Lista todos os clientes com resumo
```

## 💾 **Cache de Token Simples (Sem Redis)**

```python
# token_cache.py - Cache em arquivo local
import json
from datetime import datetime, timedelta
from pathlib import Path

class TokenCache:
    def __init__(self):
        self.cache_file = Path("token_cache.json")
    
    def get_token(self) -> str | None:
        if not self.cache_file.exists():
            return None
        
        data = json.loads(self.cache_file.read_text())
        
        # Verificar se ainda é válido (margem 5 min)
        expires_at = datetime.fromisoformat(data["expires_at"])
        if datetime.now() + timedelta(minutes=5) >= expires_at:
            return None
            
        return data["token"]
    
    def save_token(self, token: str, expires_in: int):
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        data = {
            "token": token,
            "expires_at": expires_at.isoformat()
        }
        
        self.cache_file.write_text(json.dumps(data))
```

## 🎯 **Funcionalidades APENAS de Consulta**

### **O que FAZ:**
- ✅ Consulta APIs do SERPRO Integra Contador
- ✅ Armazena dados na tabela `haylander`
- ✅ Cache simples de token OAuth
- ✅ API REST para acessar dados armazenados
- ✅ Retry automático em caso de erro

### **O que NÃO FAZ:**
- ❌ Emissão de DAS
- ❌ Geração de relatórios
- ❌ Declarações automáticas
- ❌ Processamento complexo
- ❌ Cache distribuído

## 🔧 **Fluxo Simples**

1. **Recebe CNPJ** via API
2. **Consulta token** (cache local ou novo)
3. **Chama APIs SERPRO** em paralelo:
   - PGMEI dívida ativa
   - PGDASD declarações
   - CCMEI dados
   - Caixa postal
   - Procurações
4. **Consolida dados** simples na tabela
5. **Retorna resultado** estruturado

## 🚀 **Como usar**

### **1. Instalar dependências**
```bash
pip install -r requirements.txt
```

### **2. Configurar ambiente**
```bash
cp env.example .env
# Editar .env com suas credenciais SERPRO
```

### **3. Iniciar aplicação**
```bash
python start_app.py
```
Ou manualmente:
```bash
python -m app.main
```

### **4. Acessar**
- **API**: http://localhost:8000
- **Documentação**: http://localhost:8000/docs  
- **Health Check**: http://localhost:8000/health

### **⚠️ IMPORTANTE**
- **Procuração SERPRO deve estar VÁLIDA**
- **Certificado .pfx** deve estar na pasta `certs/`
- **Credenciais** devem estar configuradas no `.env`

---

**Status**: ✅ **Pronto para uso** - Aguardando renovação da procuração SERPRO
