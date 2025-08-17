"""
Endpoints específicos para integração com n8n
"""

import uuid
import time
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Union
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from sqlalchemy.orm import Session
from loguru import logger

from app.models import (
    ConsultaClienteN8NRequest,
    ConsultaClienteResponse,
    ConsultaPendenteResponse,
    ConsultaClienteRequest,
    DadosCliente,
    ResumoConsulta
)
from app.database import get_db, format_cnpj
from app.serpro_client import get_serpro_client, SerproClient
from app.main import process_serpro_data, salvar_dados_cliente, salvar_log_consulta
from app.constants import MENSAGENS_PADRAO

router = APIRouter(prefix="/api/v1/n8n", tags=["N8N Integration"])


def criar_response_dados_incompletos(
    request_id: str,
    dados_n8n: ConsultaClienteN8NRequest
) -> ConsultaPendenteResponse:
    """Cria response quando dados estão incompletos"""
    
    dados_faltantes = []
    proximos_passos = []
    
    # Verificar o que está faltando
    if not dados_n8n.cnpj_foi_identificado():
        dados_faltantes.append("CNPJ")
        proximos_passos.append("Solicitar CNPJ do cliente")
    
    if not dados_n8n.razao_social_foi_identificada():
        dados_faltantes.append("Razão Social")
        proximos_passos.append("Solicitar razão social da empresa")
    
    # Determinar mensagem
    if len(dados_faltantes) == 2:
        message = "CNPJ e Razão Social não identificados. Necessário solicitar ao cliente."
    elif "CNPJ" in dados_faltantes:
        message = MENSAGENS_PADRAO["aguardando_cnpj"]
    elif "Razão Social" in dados_faltantes:
        message = MENSAGENS_PADRAO["aguardando_razao_social"]
    else:
        message = MENSAGENS_PADRAO["aguardando_atendente"]
    
    return ConsultaPendenteResponse(
        timestamp=datetime.utcnow(),
        request_id=request_id,
        message=message,
        dados_faltantes=dados_faltantes,
        dados_recebidos={
            "nome": dados_n8n.nome,
            "telefone": dados_n8n.telefone,
            "cnpj_recebido": dados_n8n.cnpj,
            "razao_social_recebida": dados_n8n.razao_social,
            "message": dados_n8n.message
        },
        proximos_passos=proximos_passos
    )


@router.post("/consultar", response_model=Union[ConsultaClienteResponse, ConsultaPendenteResponse])
async def consultar_cliente_n8n(
    dados_n8n: ConsultaClienteN8NRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: Session = Depends(get_db),
    serpro_client: SerproClient = Depends(get_serpro_client)
):
    """
    Endpoint principal para receber dados do n8n
    
    Recebe dados dinâmicos do n8n e decide se:
    1. Pode consultar SERPRO (dados completos)
    2. Precisa aguardar mais dados (dados incompletos)
    """
    
    start_time = time.time()
    request_id = str(uuid.uuid4())
    
    logger.info(f"Consulta n8n {request_id} - Nome: {dados_n8n.nome}, Tel: {dados_n8n.telefone}")
    logger.info(f"CNPJ: {dados_n8n.cnpj}, Razão Social: {dados_n8n.razao_social}")
    
    try:
        # Verificar se pode consultar SERPRO
        if not dados_n8n.pode_consultar_serpro():
            logger.info(f"Dados incompletos para consulta {request_id}")
            
            response = criar_response_dados_incompletos(request_id, dados_n8n)
            
            # Salvar log de dados incompletos
            tempo_resposta_ms = int((time.time() - start_time) * 1000)
            
            background_tasks.add_task(
                salvar_log_consulta,
                db, request_id, 
                ConsultaClienteRequest(
                    cnpj=dados_n8n.cnpj,
                    razao_social=dados_n8n.razao_social,
                    nome=dados_n8n.nome,
                    telefone=dados_n8n.telefone,
                    message=dados_n8n.message
                ),
                response.dict(), "DADOS_INCOMPLETOS", tempo_resposta_ms, request
            )
            
            return response
        
        # Dados completos - consultar SERPRO
        cnpj_limpo = dados_n8n.get_cnpj_limpo()
        logger.info(f"Consultando SERPRO para CNPJ: {cnpj_limpo}")
        
        # Converter para formato interno
        dados_consulta = ConsultaClienteRequest(
            cnpj=cnpj_limpo,
            razao_social=dados_n8n.razao_social,
            nome=dados_n8n.nome,
            telefone=dados_n8n.telefone,
            data_de_hoje=dados_n8n.data_de_hoje,
            message=dados_n8n.message
        )
        
        # Consultar dados no SERPRO
        serpro_data = await serpro_client.consultar_todas_informacoes(cnpj_limpo)
        
        # Processar dados recebidos
        dados_consultados = process_serpro_data(cnpj_limpo, serpro_data)
        
        # Criar response de sucesso
        dados_cliente = DadosCliente(
            cnpj=cnpj_limpo,
            cnpj_formatado=format_cnpj(cnpj_limpo),
            razao_social=dados_n8n.razao_social,
            nome=dados_n8n.nome,
            telefone=dados_n8n.telefone
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
            acoes_necessarias=acoes_necessarias,
            pode_consultar=True
        )
        
        response = ConsultaClienteResponse(
            timestamp=datetime.utcnow(),
            request_id=request_id,
            dados_cliente=dados_cliente,
            dados_consultados=dados_consultados,
            resumo=resumo,
            dados_n8n={
                "nome_original": dados_n8n.nome,
                "telefone_original": dados_n8n.telefone,
                "cnpj_original": dados_n8n.cnpj,
                "razao_social_original": dados_n8n.razao_social,
                "message_original": dados_n8n.message
            }
        )
        
        # Salvar dados em background
        tempo_resposta_ms = int((time.time() - start_time) * 1000)
        
        background_tasks.add_task(
            salvar_dados_cliente,
            db, cnpj_limpo, dados_consulta, dados_consultados
        )
        
        background_tasks.add_task(
            salvar_log_consulta,
            db, request_id, dados_consulta, response.dict(),
            "SUCCESS", tempo_resposta_ms, request
        )
        
        logger.info(f"Consulta n8n {request_id} concluída com sucesso")
        return response
        
    except Exception as e:
        logger.error(f"Erro na consulta n8n {request_id}: {e}")
        
        # Salvar erro em background
        tempo_resposta_ms = int((time.time() - start_time) * 1000)
        
        background_tasks.add_task(
            salvar_log_consulta,
            db, request_id,
            ConsultaClienteRequest(
                cnpj=dados_n8n.cnpj,
                razao_social=dados_n8n.razao_social,
                nome=dados_n8n.nome,
                telefone=dados_n8n.telefone,
                message=dados_n8n.message
            ),
            {}, "ERROR", tempo_resposta_ms, request, {"error": str(e)}
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


@router.post("/webhook")
async def webhook_n8n(
    data: Dict[str, Any],
    request: Request
):
    """
    Webhook genérico para receber dados do n8n
    Converte automaticamente para o formato esperado
    """
    
    logger.info(f"Webhook n8n recebido: {data}")
    
    try:
        # Extrair dados do webhook (formato flexível)
        nome = data.get("nome") or data.get("user", {}).get("name") or "Usuário"
        telefone = data.get("telefone") or data.get("user", {}).get("number") or ""
        data_hoje = data.get("data_de_hoje") or data.get("date") or datetime.now().strftime("%Y-%m-%d")
        cnpj = data.get("cnpj") or "se indetificado!"
        razao_social = data.get("razao_social") or "se indetificado!"
        message = data.get("message") or "aguardando atendente!"
        
        # Criar request estruturado
        dados_n8n = ConsultaClienteN8NRequest(
            nome=nome,
            telefone=telefone,
            data_de_hoje=data_hoje,
            cnpj=cnpj,
            razao_social=razao_social,
            message=message
        )
        
        # Redirecionar para endpoint principal
        return await consultar_cliente_n8n(
            dados_n8n=dados_n8n,
            background_tasks=BackgroundTasks(),
            request=request,
            db=next(get_db()),
            serpro_client=get_serpro_client()
        )
        
    except Exception as e:
        logger.error(f"Erro no webhook n8n: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao processar webhook: {str(e)}"
        )


@router.get("/status")
async def status_n8n():
    """Status da integração n8n"""
    return {
        "status": "online",
        "integration": "n8n",
        "endpoints": [
            "/api/v1/n8n/consultar - Consulta principal",
            "/api/v1/n8n/webhook - Webhook genérico"
        ],
        "formato_esperado": {
            "nome": "Nome do usuário",
            "telefone": "11999887766", 
            "cnpj": "CNPJ ou 'se indetificado!'",
            "razao_social": "Razão social ou 'se indetificado!'",
            "message": "Status atual"
        }
    } 