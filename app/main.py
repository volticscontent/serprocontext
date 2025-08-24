from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import datetime
from decimal import Decimal
from typing import List

from app.config import settings
from app.database import get_db, init_db
from app.models import Haylander
from app.schemas import (
    CNPJRequest, 
    HaylanderResponse, 
    ConsultaResponse, 
    HealthResponse
)
from app.serpro_client import serpro_client
from app.token_cache import token_cache

from loguru import logger

# Configurar logging
logger.add(
    settings.log_file,
    level=settings.log_level,
    rotation="10 MB",
    retention="30 days",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)

# Criar aplicação FastAPI
app = FastAPI(
    title="Bot e-CAC - SERPRO Integra Contador",
    description="Sistema simples para consultas automatizadas via SERPRO",
    version="1.0.0",
    debug=settings.api_debug
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar banco na startup
@app.on_event("startup")
def startup_event():
    """Inicializar aplicação"""
    logger.info("🚀 Iniciando Bot e-CAC...")
    init_db()
    logger.success("✅ Banco de dados inicializado")
    logger.info("📋 ATENÇÃO: Verifique se a procuração SERPRO está válida!")


@app.get("/", response_model=dict)
async def root():
    """Endpoint raiz"""
    return {
        "message": "🤖 Bot e-CAC - SERPRO Integra Contador",
        "version": "1.0.0",
        "status": "✅ Sistema operacional",
        "ambiente": settings.serpro_ambiente,
        "endpoints": {
            "docs": "/docs",
            "health": "/health",
            "consultar": "/consultar/{cnpj}",
            "listar": "/clientes"
        },
        "importante": "⚠️ Verifique se a procuração SERPRO está válida"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check da aplicação"""
    try:
        # Testar conexão com banco usando SQLAlchemy 2.0+ syntax
        from sqlalchemy import text
        result = db.execute(text("SELECT 1")).fetchone()
        if result and result[0] == 1:
            db_status = "connected"
        else:
            db_status = "error"
    except Exception as e:
        logger.error(f"Erro no health check do banco: {e}")
        db_status = "error"
    
    # Verificar cache de token
    cache_status = "ok" if token_cache.get_token() else "empty"
    
    return HealthResponse(
        timestamp=datetime.now(),
        database=db_status,
        serpro_cache=cache_status
    )


def consolidar_dados_serpro(cnpj: str, dados_apis: dict) -> dict:
    """Consolida dados das APIs SERPRO em estrutura simples"""
    
    # Extrair dados PGMEI
    pgmei_data = dados_apis.get("pgmei_divida", {})
    pgmei_valor = 0.00
    pgmei_tem_divida = False
    
    if pgmei_data.get("status") != "error" and pgmei_data.get("status") != "not_found":
        # Processar dados de dívida (estrutura pode variar)
        dividas = pgmei_data.get("dividas", [])
        if dividas:
            pgmei_valor = sum(float(d.get("valor", 0)) for d in dividas)
            pgmei_tem_divida = pgmei_valor > 0
    
    # Extrair dados PGDASD
    pgdasd_data = dados_apis.get("pgdasd_declaracoes", {})
    pgdasd_count = 0
    pgdasd_anos = ""
    
    if pgdasd_data.get("status") != "error" and pgdasd_data.get("status") != "not_found":
        declaracoes = pgdasd_data.get("declaracoes_pendentes", [])
        pgdasd_count = len(declaracoes)
        anos_list = [str(d.get("ano", "")) for d in declaracoes if d.get("ano")]
        pgdasd_anos = ",".join(anos_list)
    
    # Extrair dados CCMEI
    ccmei_data = dados_apis.get("ccmei_dados", {}) or dados_apis.get("ccmei_situacao", {})
    ccmei_situacao = "Não informada"
    ccmei_abertura = None
    
    if ccmei_data.get("status") != "error" and ccmei_data.get("status") != "not_found":
        ccmei_situacao = ccmei_data.get("situacao", "Ativa")
        abertura_str = ccmei_data.get("data_abertura")
        if abertura_str:
            try:
                ccmei_abertura = datetime.fromisoformat(abertura_str.replace("Z", "+00:00"))
            except:
                pass
    
    # Extrair dados Caixa Postal
    caixa_data = dados_apis.get("caixa_postal", {})
    caixa_count = 0
    caixa_nao_lidas = 0
    
    if caixa_data.get("status") != "error" and caixa_data.get("status") != "not_found":
        mensagens = caixa_data.get("mensagens", [])
        caixa_count = len(mensagens)
        caixa_nao_lidas = len([m for m in mensagens if not m.get("lida", True)])
    
    # Extrair dados Procurações
    proc_data = dados_apis.get("procuracoes", {})
    proc_ativas = 0
    
    if proc_data.get("status") != "error" and proc_data.get("status") != "not_found":
        procuracoes = proc_data.get("procuracoes", [])
        proc_ativas = len([p for p in procuracoes if p.get("ativa", False)])
    
    # Calcular situação geral
    valor_total = pgmei_valor
    situacao_geral = "OK"
    
    if pgmei_tem_divida or pgdasd_count > 0 or caixa_nao_lidas > 0:
        situacao_geral = "PENDENCIAS"
    
    if pgmei_valor > 1000 or pgdasd_count > 3:
        situacao_geral = "PROBLEMAS"
    
    return {
        "pgmei_divida_valor": Decimal(str(pgmei_valor)),
        "pgmei_tem_divida": pgmei_tem_divida,
        "pgmei_ultimo_update": datetime.now(),
        
        "pgdasd_pendentes_count": pgdasd_count,
        "pgdasd_anos_pendentes": pgdasd_anos,
        "pgdasd_ultimo_update": datetime.now(),
        
        "ccmei_situacao": ccmei_situacao,
        "ccmei_data_abertura": ccmei_abertura,
        "ccmei_ultimo_update": datetime.now(),
        
        "caixa_mensagens_count": caixa_count,
        "caixa_mensagens_nao_lidas": caixa_nao_lidas,
        "caixa_ultimo_update": datetime.now(),
        
        "procuracoes_ativas": proc_ativas,
        "procuracoes_ultimo_update": datetime.now(),
        
        "situacao_geral": situacao_geral,
        "valor_total_pendente": Decimal(str(valor_total)),
        "ultima_consulta": datetime.now(),
        "status_consulta": "SUCCESS"
    }


@app.post("/consultar/{cnpj}", response_model=ConsultaResponse)
async def consultar_cliente(
    cnpj: str, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Consulta completa de um cliente via SERPRO"""
    
    # Validar CNPJ
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        raise HTTPException(status_code=400, detail="CNPJ deve ter 14 dígitos")
    
    try:
        logger.info(f"🔍 Iniciando consulta para CNPJ: {cnpj_limpo}")
        
        # Consultar todas as APIs SERPRO
        dados_apis = await serpro_client.consultar_todas_apis(cnpj_limpo)
        
        # Consolidar dados
        dados_consolidados = consolidar_dados_serpro(cnpj_limpo, dados_apis)
        
        # Buscar ou criar registro na tabela
        cliente = db.query(Haylander).filter(Haylander.cnpj == cnpj_limpo).first()
        
        if cliente:
            # Atualizar registro existente
            for campo, valor in dados_consolidados.items():
                setattr(cliente, campo, valor)
            cliente.updated_at = datetime.now()
        else:
            # Criar novo registro
            dados_consolidados["cnpj"] = cnpj_limpo
            dados_consolidados["created_at"] = datetime.now()
            cliente = Haylander(**dados_consolidados)
            db.add(cliente)
        
        db.commit()
        db.refresh(cliente)
        
        logger.success(f"✅ Consulta finalizada para CNPJ: {cnpj_limpo}")
        
        return ConsultaResponse(
            success=True,
            message="✅ Consulta realizada com sucesso",
            cnpj=cnpj_limpo,
            dados=HaylanderResponse.from_orm(cliente)
        )
        
    except Exception as e:
        error_msg = str(e)
        
        # Detectar se é erro de procuração
        if "403" in error_msg or "forbidden" in error_msg.lower():
            logger.error(f"🚫 PROCURAÇÃO EXPIRADA para CNPJ {cnpj_limpo}: {e}")
            error_detail = "Procuração SERPRO expirada - Renovar procuração"
        elif "404" in error_msg or "not found" in error_msg.lower():
            logger.error(f"📋 API não encontrada para CNPJ {cnpj_limpo}: {e}")
            error_detail = "API não encontrada - Verificar acesso SERPRO"
        else:
            logger.error(f"❌ Erro na consulta para CNPJ {cnpj_limpo}: {e}")
            error_detail = f"Erro interno: {error_msg}"
        
        # Tentar salvar erro na base
        try:
            cliente = db.query(Haylander).filter(Haylander.cnpj == cnpj_limpo).first()
            if cliente:
                cliente.status_consulta = "ERROR"
                cliente.ultima_consulta = datetime.now()
                db.commit()
        except:
            pass
        
        return ConsultaResponse(
            success=False,
            message=error_detail,
            cnpj=cnpj_limpo,
            errors=[error_detail]
        )


@app.get("/cliente/{cnpj}", response_model=HaylanderResponse)
async def obter_dados_cliente(cnpj: str, db: Session = Depends(get_db)):
    """Obtém dados consolidados de um cliente"""
    
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    if len(cnpj_limpo) != 14:
        raise HTTPException(status_code=400, detail="CNPJ deve ter 14 dígitos")
    
    cliente = db.query(Haylander).filter(Haylander.cnpj == cnpj_limpo).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return HaylanderResponse.from_orm(cliente)


@app.get("/clientes", response_model=List[HaylanderResponse])
async def listar_clientes(
    limit: int = 50, 
    offset: int = 0, 
    db: Session = Depends(get_db)
):
    """Lista todos os clientes com paginação"""
    
    clientes = db.query(Haylander).offset(offset).limit(limit).all()
    
    return [HaylanderResponse.from_orm(cliente) for cliente in clientes]


@app.delete("/cliente/{cnpj}")
async def deletar_cliente(cnpj: str, db: Session = Depends(get_db)):
    """Remove um cliente da base"""
    
    cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
    cliente = db.query(Haylander).filter(Haylander.cnpj == cnpj_limpo).first()
    
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    db.delete(cliente)
    db.commit()
    
    return {"message": "Cliente removido com sucesso"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    ) 