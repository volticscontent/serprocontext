"""
API Bot e-CAC - Aplicação Principal
"""

import uuid
import time
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from loguru import logger

from app.config import get_settings
from app.models import (
    ConsultaClienteRequest,
    ConsultaClienteResponse, 
    ErrorResponse,
    HealthResponse,
    StatusResponse,
    DadosCliente,
    DadosConsultados,
    DadosMEI,
    DadosCadastro,
    DadosDividas,
    DadosDeclaracoes,
    DeclaracaoInfo,
    ResumoConsulta,
    AtividadePrincipal
)
from app.database import (
    get_db, 
    format_cnpj,
    get_cliente_by_cnpj,
    create_cliente,
    update_cliente,
    create_consulta_log,
    Cliente,
    ConsultaLog
)
from app.serpro_client import get_serpro_client, SerproClient
from app.endpoints_n8n import router as n8n_router

settings = get_settings()

# Configuração da aplicação FastAPI
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.api_debug,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=["*"],
)

# Incluir routers
app.include_router(n8n_router)

# Configurar logging
logger.add(
    settings.log_file,
    rotation="10 MB",
    retention="30 days",
    level=settings.log_level,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} | {message}"
)


# Middleware para logging de requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response


def create_error_response(
    code: str, 
    message: str, 
    details: list = None,
    request_id: str = None
) -> ErrorResponse:
    """Cria response de erro padronizado"""
    return ErrorResponse(
        error={
            "code": code,
            "message": message,
            "details": details or []
        },
        timestamp=datetime.utcnow(),
        request_id=request_id or str(uuid.uuid4())
    )


def process_serpro_data(cnpj: str, serpro_data: Dict[str, Any]) -> DadosConsultados:
    """Processa dados do SERPRO e converte para o formato da API"""
    
    # Dados MEI
    mei_data = DadosMEI()
    
    # Processar PGMEI
    if "pgmei_divida_ativa" in serpro_data.get("consultas", {}):
        pgmei = serpro_data["consultas"]["pgmei_divida_ativa"]
        if pgmei.get("success"):
            data = pgmei.get("data", {})
            if "data" in data:
                dividas = data["data"].get("dividas", [])
                valor_total = data["data"].get("valor_total_dividas", 0)
                mei_data.valor_total_guias_abertas = Decimal(str(valor_total))
    
    # Processar CCMEI
    if "ccmei_situacao" in serpro_data.get("consultas", {}):
        ccmei = serpro_data["consultas"]["ccmei_situacao"]
        if ccmei.get("success"):
            data = ccmei.get("data", {})
            if "data" in data:
                situacao = data["data"].get("situacao", "")
                mei_data.situacao = situacao
                mei_data.is_mei = "MEI" in situacao.upper()
    
    # Processar PGDASD
    declaracoes_pendentes = []
    if "pgdasd_declaracoes" in serpro_data.get("consultas", {}):
        pgdasd = serpro_data["consultas"]["pgdasd_declaracoes"]
        if pgdasd.get("success"):
            data = pgdasd.get("data", {})
            if "data" in data:
                declaracoes = data["data"].get("declaracoes", [])
                for decl in declaracoes:
                    if decl.get("situacao") == "PENDENTE":
                        periodo = decl.get("periodo", "")
                        if periodo and len(periodo) >= 4:
                            ano = periodo[:4]
                            if ano not in declaracoes_pendentes:
                                declaracoes_pendentes.append(ano)
    
    mei_data.anos_declaracoes_pendentes = declaracoes_pendentes
    
    # Dados cadastrais (placeholder)
    cadastro_data = DadosCadastro(
        estado="SP",  # Será obtido de outras fontes
        municipio="São Paulo",
        atividade_principal=AtividadePrincipal(
            codigo="6201-5/00",
            descricao="Desenvolvimento de programas de computador sob encomenda"
        ),
        email="contato@exemplo.com"
    )
    
    # Dados de dívidas
    dividas_data = DadosDividas()
    if mei_data.valor_total_guias_abertas:
        dividas_data.divida_ativa_uniao = mei_data.valor_total_guias_abertas
        dividas_data.total_dividas = mei_data.valor_total_guias_abertas
    
    # Dados de declarações
    declaracoes_data = DadosDeclaracoes(
        mei=DeclaracaoInfo(
            possui=True,
            anos_pendentes=declaracoes_pendentes
        ),
        simples_nacional=DeclaracaoInfo(
            possui=True,
            anos_pendentes=declaracoes_pendentes
        )
    )
    
    return DadosConsultados(
        mei=mei_data,
        cadastro=cadastro_data,
        dividas=dividas_data,
        declaracoes=declaracoes_data
    )


async def salvar_dados_cliente(
    db: Session,
    cnpj: str,
    dados_request: ConsultaClienteRequest,
    dados_consultados: DadosConsultados
):
    """Salva ou atualiza dados do cliente no banco"""
    try:
        # Buscar cliente existente
        cliente = get_cliente_by_cnpj(db, cnpj)
        
        cliente_data = {
            "cnpj": cnpj,
            "cnpj_formatado": format_cnpj(cnpj),
            "razao_social": dados_request.razao_social,
            "is_mei": dados_consultados.mei.is_mei,
            "situacao": dados_consultados.mei.situacao,
            "estado": dados_consultados.cadastro.estado,
            "municipio": dados_consultados.cadastro.municipio,
            "email": dados_consultados.cadastro.email,
            "telefone": dados_request.telefone,
            "status_geral": "PENDENCIAS" if dados_consultados.mei.anos_declaracoes_pendentes else "OK",
            "ultima_consulta": datetime.utcnow(),
            "dados_completos": {
                "mei": dados_consultados.mei.dict(),
                "cadastro": dados_consultados.cadastro.dict(),
                "dividas": dados_consultados.dividas.dict(),
                "declaracoes": dados_consultados.declaracoes.dict() if dados_consultados.declaracoes else None
            }
        }
        
        if cliente:
            update_cliente(db, cnpj, cliente_data)
        else:
            create_cliente(db, cliente_data)
            
        logger.info(f"Dados do cliente {cnpj} salvos no banco")
        
    except Exception as e:
        logger.error(f"Erro ao salvar dados do cliente {cnpj}: {e}")


def salvar_log_consulta(
    db: Session,
    request_id: str,
    dados_request: ConsultaClienteRequest,
    response_data: Dict[str, Any],
    status: str,
    tempo_resposta_ms: int,
    request: Request,
    error_log: Dict[str, Any] = None
):
    """Salva log da consulta no banco"""
    try:
        log_data = {
            "request_id": request_id,
            "cnpj": dados_request.cnpj,
            "razao_social": dados_request.razao_social,
            "nome_cliente": dados_request.nome,
            "telefone": dados_request.telefone,
            "data_consulta": datetime.utcnow(),
            "status": status,
            "tempo_resposta_ms": tempo_resposta_ms,
            "ip_origem": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent"),
            "dados_request": dados_request.dict(),
            "dados_response": response_data,
            "errors_log": error_log
        }
        
        create_consulta_log(db, log_data)
        logger.info(f"Log da consulta {request_id} salvo")
        
    except Exception as e:
        logger.error(f"Erro ao salvar log da consulta {request_id}: {e}")


# Endpoints da API

@app.get("/", include_in_schema=False)
async def root():
    """Endpoint raiz"""
    return {
        "message": "Bot e-CAC API",
        "version": settings.api_version,
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check(
    serpro_client: SerproClient = Depends(get_serpro_client),
    db: Session = Depends(get_db)
):
    """Health check da API"""
    
    # Verificar SERPRO
    serpro_status = await serpro_client.health_check()
    
    # Verificar banco de dados
    try:
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return HealthResponse(
        status="healthy" if serpro_status["status"] == "connected" and db_status == "connected" else "unhealthy",
        integra_contador=serpro_status["status"],
        database=db_status,
        timestamp=datetime.utcnow(),
        version=settings.api_version
    )


@app.get("/status/{cnpj}", response_model=StatusResponse)
async def consultar_status_rapido(
    cnpj: str,
    db: Session = Depends(get_db)
):
    """Consulta status rápido de um CNPJ"""
    
    # Buscar no banco
    cliente = get_cliente_by_cnpj(db, cnpj)
    
    if not cliente:
        raise HTTPException(
            status_code=404,
            detail="CNPJ não encontrado na base de dados"
        )
    
    return StatusResponse(
        cnpj=cnpj,
        is_mei=cliente.is_mei,
        situacao=cliente.situacao or "DESCONHECIDO",
        tem_pendencias=cliente.status_geral == "PENDENCIAS"
    )


@app.post("/api/v1/consultar-cliente", response_model=ConsultaClienteResponse)
async def consultar_cliente(
    dados_request: ConsultaClienteRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    serpro_client: SerproClient = Depends(get_serpro_client)
):
    """Endpoint principal - Consulta dados do cliente no e-CAC"""
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    logger.info(f"Iniciando consulta {request_id} para CNPJ: {dados_request.cnpj}")
    
    try:
        # Consultar dados no SERPRO
        serpro_data = await serpro_client.consultar_todas_informacoes(dados_request.cnpj)
        
        # Processar dados recebidos
        dados_consultados = process_serpro_data(dados_request.cnpj, serpro_data)
        
        # Criar response
        dados_cliente = DadosCliente(
            cnpj=dados_request.cnpj,
            cnpj_formatado=format_cnpj(dados_request.cnpj),
            razao_social=dados_request.razao_social,
            nome=dados_request.nome,
            telefone=dados_request.telefone
        )
        
        # Criar resumo
        total_devido = dados_consultados.dividas.total_dividas
        acoes_necessarias = []
        
        if dados_consultados.mei.anos_declaracoes_pendentes:
            anos_str = ", ".join(dados_consultados.mei.anos_declaracoes_pendentes)
            acoes_necessarias.append(f"Regularizar declarações MEI {anos_str}")
        
        if total_devido > 0:
            acoes_necessarias.append("Quitar guias em aberto")
        
        status_geral = "PENDENCIAS" if acoes_necessarias else "OK"
        
        resumo = ResumoConsulta(
            status_geral=status_geral,
            total_devido=total_devido,
            acoes_necessarias=acoes_necessarias
        )
        
        response = ConsultaClienteResponse(
            timestamp=datetime.utcnow(),
            request_id=request_id,
            dados_cliente=dados_cliente,
            dados_consultados=dados_consultados,
            resumo=resumo
        )
        
        # Salvar dados em background
        tempo_resposta_ms = int((time.time() - start_time) * 1000)
        
        background_tasks.add_task(
            salvar_dados_cliente,
            db, dados_request.cnpj, dados_request, dados_consultados
        )
        
        background_tasks.add_task(
            salvar_log_consulta,
            db, request_id, dados_request, response.dict(),
            "SUCCESS", tempo_resposta_ms, request
        )
        
        logger.info(f"Consulta {request_id} concluída com sucesso")
        return response
        
    except Exception as e:
        logger.error(f"Erro na consulta {request_id}: {e}")
        
        # Salvar erro em background
        tempo_resposta_ms = int((time.time() - start_time) * 1000)
        
        background_tasks.add_task(
            salvar_log_consulta,
            db, request_id, dados_request, {},
            "ERROR", tempo_resposta_ms, request, {"error": str(e)}
        )
        
        # Retornar erro apropriado
        if "401" in str(e) or "token" in str(e).lower():
            raise HTTPException(
                status_code=401,
                detail="Erro de autenticação com SERPRO"
            )
        elif "404" in str(e):
            raise HTTPException(
                status_code=404,
                detail="CNPJ não encontrado"
            )
        elif "timeout" in str(e).lower():
            raise HTTPException(
                status_code=503,
                detail="Timeout na consulta ao SERPRO"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Erro interno: {str(e)}"
            )


@app.post("/api/v1/consultar-teste")
async def consultar_teste():
    """Endpoint de teste com dados fictícios"""
    
    request_id = str(uuid.uuid4())
    
    # Dados fictícios para teste
    dados_cliente = DadosCliente(
        cnpj=settings.cnpj_teste,
        cnpj_formatado=format_cnpj(settings.cnpj_teste),
        razao_social=settings.razao_social_teste,
        nome="Gustavo Souza",
        telefone="11999887766"
    )
    
    dados_consultados = DadosConsultados(
        mei=DadosMEI(
            is_mei=True,
            situacao="ATIVO",
            valor_total_guias_abertas=Decimal("245.40"),
            anos_declaracoes_pendentes=["2023", "2024"]
        ),
        cadastro=DadosCadastro(
            estado="SP",
            municipio="São Paulo",
            atividade_principal=AtividadePrincipal(
                codigo="6201-5/00",
                descricao="Desenvolvimento de programas de computador sob encomenda"
            ),
            email="gustavo@exemplo.com"
        ),
        dividas=DadosDividas(
            divida_ativa_uniao=Decimal("245.40"),
            total_dividas=Decimal("245.40")
        ),
        declaracoes=DadosDeclaracoes(
            mei=DeclaracaoInfo(
                possui=True,
                anos_pendentes=["2023", "2024"]
            )
        )
    )
    
    resumo = ResumoConsulta(
        status_geral="PENDENCIAS",
        total_devido=Decimal("245.40"),
        acoes_necessarias=[
            "Regularizar declarações MEI 2023 e 2024",
            "Quitar guias em aberto"
        ]
    )
    
    return ConsultaClienteResponse(
        timestamp=datetime.utcnow(),
        request_id=request_id,
        dados_cliente=dados_cliente,
        dados_consultados=dados_consultados,
        resumo=resumo
    )


# Handler global de erros
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Erro não tratado: {exc}")
    
    return JSONResponse(
        status_code=500,
        content=create_error_response(
            "INTERNAL_ERROR",
            "Erro interno do servidor",
            [str(exc)]
        ).dict()
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug
    ) 