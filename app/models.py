"""
Models Pydantic para API Bot e-CAC
"""

from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from decimal import Decimal
from pydantic import BaseModel, Field, validator
import re


def validate_cnpj(cnpj: str) -> str:
    """Valida e limpa CNPJ"""
    if not cnpj:
        raise ValueError("CNPJ é obrigatório")
    
    # Remove formatação
    clean_cnpj = re.sub(r'[^\d]', '', cnpj)
    
    if len(clean_cnpj) != 14:
        raise ValueError("CNPJ deve ter 14 dígitos")
    
    return clean_cnpj


def is_cnpj_identificado(cnpj: str) -> bool:
    """Verifica se CNPJ foi identificado (não é placeholder)"""
    if not cnpj:
        return False
    
    placeholders = [
        "se indetificado!",
        "se identificado!", 
        "nao identificado",
        "não identificado",
        "aguardando",
        "pendente"
    ]
    
    cnpj_lower = cnpj.lower().strip()
    return not any(placeholder in cnpj_lower for placeholder in placeholders)


def is_razao_social_identificada(razao_social: str) -> bool:
    """Verifica se razão social foi identificada (não é placeholder)"""
    if not razao_social:
        return False
    
    placeholders = [
        "se indetificado!",
        "se identificado!",
        "nao identificado", 
        "não identificado",
        "aguardando",
        "pendente"
    ]
    
    razao_lower = razao_social.lower().strip()
    return not any(placeholder in razao_lower for placeholder in placeholders)


class ConsultaClienteN8NRequest(BaseModel):
    """Request vindo do n8n com dados dinâmicos"""
    nome: str = Field(..., description="Nome do usuário do WhatsApp")
    telefone: str = Field(..., description="Número do WhatsApp")
    data_de_hoje: Optional[str] = Field(None, description="Data atual")
    cnpj: str = Field(..., description="CNPJ (pode ser placeholder se não identificado)")
    razao_social: str = Field(..., description="Razão social (pode ser placeholder se não identificada)")
    message: str = Field(..., description="Mensagem/status atual")
    
    @validator('telefone')
    def limpar_telefone(cls, v):
        """Remove formatação do telefone"""
        if v:
            return re.sub(r'[^\d]', '', v)
        return v
    
    def cnpj_foi_identificado(self) -> bool:
        """Verifica se CNPJ foi identificado pelo n8n"""
        return is_cnpj_identificado(self.cnpj)
    
    def razao_social_foi_identificada(self) -> bool:
        """Verifica se razão social foi identificada pelo n8n"""
        return is_razao_social_identificada(self.razao_social)
    
    def pode_consultar_serpro(self) -> bool:
        """Verifica se tem dados suficientes para consultar SERPRO"""
        return self.cnpj_foi_identificado() and self.razao_social_foi_identificada()
    
    def get_cnpj_limpo(self) -> Optional[str]:
        """Retorna CNPJ limpo se foi identificado"""
        if self.cnpj_foi_identificado():
            return re.sub(r'[^\d]', '', self.cnpj)
        return None


class ConsultaClienteRequest(BaseModel):
    """Request para consulta de cliente (formato interno)"""
    cnpj: str = Field(..., description="CNPJ do cliente (14 dígitos)")
    razao_social: str = Field(..., description="Razão social do cliente")
    nome: Optional[str] = Field(None, description="Nome do contato")
    telefone: Optional[str] = Field(None, description="Telefone do contato")
    data_de_hoje: Optional[str] = Field(None, description="Data da consulta (YYYY-MM-DD)")
    message: Optional[str] = Field(None, description="Mensagem adicional")
    
    @validator('cnpj')
    def validate_cnpj_field(cls, v):
        return validate_cnpj(v)


class AtividadePrincipal(BaseModel):
    """Atividade principal da empresa"""
    codigo: str
    descricao: str


class DadosCadastro(BaseModel):
    """Dados cadastrais do cliente"""
    estado: Optional[str] = None
    municipio: Optional[str] = None
    cep: Optional[str] = None
    atividade_principal: Optional[AtividadePrincipal] = None
    email: Optional[str] = None


class DadosMEI(BaseModel):
    """Dados específicos do MEI"""
    is_mei: bool = False
    situacao: Optional[str] = None
    data_abertura: Optional[date] = None
    valor_total_guias_abertas: Decimal = Field(default=Decimal('0.00'))
    anos_declaracoes_pendentes: List[str] = Field(default_factory=list)
    ano_exclusao_mei: Optional[str] = None
    ano_exclusao_simples: Optional[str] = None


class DadosDividas(BaseModel):
    """Dados de dívidas ativas"""
    divida_ativa_uniao: Decimal = Field(default=Decimal('0.00'))
    divida_ativa_estado: Decimal = Field(default=Decimal('0.00'))
    divida_ativa_municipio: Decimal = Field(default=Decimal('0.00'))
    total_dividas: Decimal = Field(default=Decimal('0.00'))


class DeclaracaoInfo(BaseModel):
    """Informações de declaração"""
    possui: bool = False
    anos_pendentes: List[str] = Field(default_factory=list)


class DadosDeclaracoes(BaseModel):
    """Dados de declarações"""
    simples_nacional: Optional[DeclaracaoInfo] = None
    mei: Optional[DeclaracaoInfo] = None


class DadosConsultados(BaseModel):
    """Dados consultados no e-CAC"""
    mei: DadosMEI
    cadastro: DadosCadastro
    dividas: DadosDividas
    declaracoes: Optional[DadosDeclaracoes] = None


class DadosCliente(BaseModel):
    """Dados do cliente fornecidos"""
    cnpj: str
    cnpj_formatado: str
    razao_social: str
    nome: Optional[str] = None
    telefone: Optional[str] = None


class ResumoConsulta(BaseModel):
    """Resumo da consulta"""
    status_geral: str  # OK, PENDENCIAS, IRREGULAR, DADOS_INCOMPLETOS
    total_devido: Decimal = Field(default=Decimal('0.00'))
    acoes_necessarias: List[str] = Field(default_factory=list)
    pode_consultar: bool = True


class ConsultaClienteResponse(BaseModel):
    """Response da consulta de cliente"""
    success: bool = True
    timestamp: datetime
    request_id: str
    dados_cliente: DadosCliente
    dados_consultados: Optional[DadosConsultados] = None
    resumo: ResumoConsulta
    dados_n8n: Optional[Dict[str, Any]] = None  # Dados originais do n8n


class ConsultaPendenteResponse(BaseModel):
    """Response quando dados estão incompletos"""
    success: bool = False
    timestamp: datetime
    request_id: str
    status: str = "DADOS_INCOMPLETOS"
    message: str
    dados_faltantes: List[str]
    dados_recebidos: Dict[str, Any]
    proximos_passos: List[str]


class ErrorDetail(BaseModel):
    """Detalhes do erro"""
    code: str
    message: str
    details: List[str] = Field(default_factory=list)


class ErrorResponse(BaseModel):
    """Response de erro"""
    success: bool = False
    error: ErrorDetail
    timestamp: datetime
    request_id: str


class HealthResponse(BaseModel):
    """Response do health check"""
    status: str = "healthy"
    integra_contador: str = "connected"
    database: str = "connected"
    timestamp: datetime
    version: str


class StatusResponse(BaseModel):
    """Response do status rápido"""
    cnpj: str
    is_mei: bool
    situacao: str
    tem_pendencias: bool


# Models para banco de dados

class ClienteDB(BaseModel):
    """Model do cliente no banco"""
    id: Optional[int] = None
    cnpj: str
    cnpj_formatado: str
    razao_social: str
    nome_fantasia: Optional[str] = None
    is_mei: bool = False
    situacao: Optional[str] = None
    data_abertura: Optional[date] = None
    estado: Optional[str] = None
    municipio: Optional[str] = None
    cep: Optional[str] = None
    atividade_principal_codigo: Optional[str] = None
    atividade_principal_descricao: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    status_geral: Optional[str] = None
    ultima_consulta: Optional[datetime] = None
    dados_completos: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConsultaLogDB(BaseModel):
    """Model do log de consulta"""
    id: Optional[int] = None
    request_id: str
    cnpj: str
    razao_social: Optional[str] = None
    nome_cliente: Optional[str] = None
    telefone: Optional[str] = None
    data_consulta: datetime
    status: str = "SUCCESS"
    tempo_resposta_ms: Optional[int] = None
    ip_origem: Optional[str] = None
    user_agent: Optional[str] = None
    dados_request: Optional[Dict[str, Any]] = None
    dados_response: Optional[Dict[str, Any]] = None
    errors_log: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class DividaAtivaDB(BaseModel):
    """Model de dívida ativa no banco"""
    id: Optional[int] = None
    cliente_id: int
    cnpj: str
    tipo_divida: str  # UNIAO, ESTADO, MUNICIPIO, MEI
    numero_inscricao: Optional[str] = None
    periodo: Optional[str] = None
    valor_principal: Decimal = Decimal('0.00')
    valor_multa: Decimal = Decimal('0.00')
    valor_juros: Decimal = Decimal('0.00')
    valor_total: Decimal = Decimal('0.00')
    situacao: str = "ATIVA"
    data_vencimento: Optional[date] = None
    data_inclusao: Optional[date] = None
    origem: Optional[str] = None
    dados_completos: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ConfiguracaoDB(BaseModel):
    """Model de configuração"""
    id: Optional[int] = None
    chave: str
    valor: Optional[str] = None
    descricao: Optional[str] = None
    tipo: str = "STRING"
    categoria: str = "SISTEMA"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None 