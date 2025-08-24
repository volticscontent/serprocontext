from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CNPJRequest(BaseModel):
    """Request para consulta por CNPJ"""
    cnpj: str = Field(..., description="CNPJ no formato 14 dígitos")
    
    @validator('cnpj')
    def validate_cnpj(cls, v):
        # Remove formatação
        cnpj = ''.join(filter(str.isdigit, v))
        
        if len(cnpj) != 14:
            raise ValueError('CNPJ deve ter exatamente 14 dígitos')
        
        # Validação básica de CNPJ (verificar se não são todos iguais)
        if len(set(cnpj)) == 1:
            raise ValueError('CNPJ inválido: não pode ter todos os dígitos iguais')
        
        return cnpj


class HaylanderResponse(BaseModel):
    """Resposta com dados consolidados do cliente"""
    
    # Identificação
    id: int
    cnpj: str
    razao_social: Optional[str] = None
    
    # PGMEI
    pgmei_divida_valor: Optional[Decimal] = 0.00
    pgmei_tem_divida: bool = False
    pgmei_ultimo_update: Optional[datetime] = None
    
    # PGDASD
    pgdasd_pendentes_count: int = 0
    pgdasd_anos_pendentes: Optional[str] = None
    pgdasd_ultimo_update: Optional[datetime] = None
    
    # CCMEI
    ccmei_situacao: Optional[str] = None
    ccmei_data_abertura: Optional[datetime] = None
    ccmei_ultimo_update: Optional[datetime] = None
    
    # Caixa Postal
    caixa_mensagens_count: int = 0
    caixa_mensagens_nao_lidas: int = 0
    caixa_ultimo_update: Optional[datetime] = None
    
    # Procurações
    procuracoes_ativas: int = 0
    procuracoes_ultimo_update: Optional[datetime] = None
    
    # Consolidação
    situacao_geral: Optional[str] = None
    valor_total_pendente: Optional[Decimal] = 0.00
    ultima_consulta: Optional[datetime] = None
    status_consulta: Optional[str] = None
    
    # Timestamps
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class ConsultaResponse(BaseModel):
    """Resposta da consulta completa"""
    success: bool
    message: str
    cnpj: str
    dados: Optional[HaylanderResponse] = None
    errors: Optional[List[str]] = None
    
    
class SerproTokenResponse(BaseModel):
    """Resposta do token OAuth SERPRO"""
    access_token: str
    token_type: str
    expires_in: int


class SerproAPIError(BaseModel):
    """Erro da API SERPRO"""
    codigo: Optional[str] = None
    mensagem: str
    detalhes: Optional[str] = None


class HealthResponse(BaseModel):
    """Resposta do health check"""
    status: str = "ok"
    timestamp: datetime
    version: str = "1.0.0"
    database: str = "connected"
    serpro_cache: str = "ok" 