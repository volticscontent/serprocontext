"""
Conexão com banco de dados PostgreSQL
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Date, Numeric, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import INET
from datetime import datetime
import json
from app.config import get_settings

settings = get_settings()

# Engine do SQLAlchemy
engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.api_debug
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para models
Base = declarative_base()


def get_db():
    """Dependency para obter sessão do banco"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Models SQLAlchemy

class Cliente(Base):
    """Tabela de clientes"""
    __tablename__ = "clientes"
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(14), unique=True, nullable=False, index=True)
    cnpj_formatado = Column(String(18))
    razao_social = Column(String(255), nullable=False)
    nome_fantasia = Column(String(255))
    is_mei = Column(Boolean, default=False)
    situacao = Column(String(50))
    data_abertura = Column(Date)
    estado = Column(String(2))
    municipio = Column(String(100))
    cep = Column(String(10))
    atividade_principal_codigo = Column(String(20))
    atividade_principal_descricao = Column(Text)
    email = Column(String(255))
    telefone = Column(String(20))
    status_geral = Column(String(50))
    ultima_consulta = Column(DateTime)
    dados_completos = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConsultaLog(Base):
    """Tabela de log de consultas"""
    __tablename__ = "consultas_log"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(50), unique=True, nullable=False)
    cnpj = Column(String(14), nullable=False, index=True)
    razao_social = Column(String(255))
    nome_cliente = Column(String(255))
    telefone = Column(String(20))
    data_consulta = Column(DateTime, default=datetime.utcnow, index=True)
    status = Column(String(20), default="SUCCESS", index=True)
    tempo_resposta_ms = Column(Integer)
    ip_origem = Column(INET)
    user_agent = Column(Text)
    dados_request = Column(JSON)
    dados_response = Column(JSON)
    errors_log = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DividaAtiva(Base):
    """Tabela de dívidas ativas"""
    __tablename__ = "dividas_ativas"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False, index=True)
    cnpj = Column(String(14), nullable=False, index=True)
    tipo_divida = Column(String(20), index=True)  # UNIAO, ESTADO, MUNICIPIO, MEI
    numero_inscricao = Column(String(50))
    periodo = Column(String(10))  # YYYY-MM
    valor_principal = Column(Numeric(15, 2), default=0.00)
    valor_multa = Column(Numeric(15, 2), default=0.00)
    valor_juros = Column(Numeric(15, 2), default=0.00)
    valor_total = Column(Numeric(15, 2), default=0.00)
    situacao = Column(String(20), default="ATIVA", index=True)
    data_vencimento = Column(Date)
    data_inclusao = Column(Date)
    origem = Column(String(50))
    dados_completos = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Declaracao(Base):
    """Tabela de declarações"""
    __tablename__ = "declaracoes"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False, index=True)
    cnpj = Column(String(14), nullable=False, index=True)
    tipo = Column(String(20), index=True)  # PGDASD, MEI, DCTFWEB, DEFIS
    periodo = Column(String(10))  # YYYY-MM
    ano = Column(Integer)
    situacao = Column(String(30), index=True)  # TRANSMITIDA, PENDENTE, RETIFICADA
    data_transmissao = Column(DateTime)
    data_vencimento = Column(Date)
    recibo = Column(String(50))
    valor_devido = Column(Numeric(15, 2), default=0.00)
    valor_pago = Column(Numeric(15, 2), default=0.00)
    em_atraso = Column(Boolean, default=False)
    dados_declaracao = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GuiaMEI(Base):
    """Tabela de guias MEI"""
    __tablename__ = "guias_mei"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False, index=True)
    cnpj = Column(String(14), nullable=False, index=True)
    periodo = Column(String(10))  # YYYY-MM
    tipo_guia = Column(String(20))  # DAS_MEI, DAS_SIMPLES
    codigo_barras = Column(String(48))
    linha_digitavel = Column(String(48))
    valor = Column(Numeric(10, 2), nullable=False)
    data_vencimento = Column(Date)
    data_pagamento = Column(Date)
    situacao = Column(String(20), default="PENDENTE")  # PENDENTE, PAGO, VENCIDO
    pdf_base64 = Column(Text)
    dados_completos = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CaixaPostal(Base):
    """Tabela de caixa postal"""
    __tablename__ = "caixa_postal"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False, index=True)
    cnpj = Column(String(14), nullable=False, index=True)
    id_mensagem = Column(String(50), unique=True, nullable=False)
    assunto = Column(String(500))
    remetente = Column(String(255))
    conteudo = Column(Text)
    data_envio = Column(DateTime, index=True)
    status = Column(String(20), default="NAO_LIDA", index=True)  # LIDA, NAO_LIDA
    prioridade = Column(String(10))  # ALTA, MEDIA, BAIXA
    tem_anexo = Column(Boolean, default=False)
    prazo_resposta = Column(Date)
    categoria = Column(String(50))  # INTIMACAO, NOTIFICACAO, INFORMATIVO
    dados_anexos = Column(JSON)
    dados_completos = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Parcelamento(Base):
    """Tabela de parcelamentos"""
    __tablename__ = "parcelamentos"
    
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False, index=True)
    cnpj = Column(String(14), nullable=False, index=True)
    numero_parcelamento = Column(String(50), unique=True, nullable=False)
    tipo = Column(String(20))  # PARCSN, PARCMEI, PERTSN, RELPSN
    situacao = Column(String(20), default="ATIVO")  # ATIVO, QUITADO, CANCELADO
    valor_total = Column(Numeric(15, 2))
    quantidade_parcelas = Column(Integer)
    parcelas_pagas = Column(Integer, default=0)
    data_primeira_parcela = Column(Date)
    dados_parcelas = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Procuracao(Base):
    """Tabela de procurações"""
    __tablename__ = "procuracoes"
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(14), nullable=False, index=True)
    cpf_procurador = Column(String(11), nullable=False)
    nome_procurador = Column(String(255))
    servicos_autorizados = Column(JSON)
    data_inicio = Column(Date)
    data_fim = Column(Date)
    ativa = Column(Boolean, default=True)
    dados_completos = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Configuracao(Base):
    """Tabela de configurações"""
    __tablename__ = "configuracoes"
    
    id = Column(Integer, primary_key=True, index=True)
    chave = Column(String(100), unique=True, nullable=False)
    valor = Column(Text)
    descricao = Column(Text)
    tipo = Column(String(20), default="STRING")  # STRING, INTEGER, BOOLEAN, JSON
    categoria = Column(String(50), default="SISTEMA")  # API, SISTEMA, SERPRO
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Haylander(Base):
    """Tabela específica Haylander"""
    __tablename__ = "haylander"
    
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(14), unique=True, nullable=False, index=True)
    razao_social = Column(String(255), nullable=False)
    situacao_mei = Column(String(50))
    valor_dividas = Column(Numeric(15, 2), default=0.00)
    declaracoes_pendentes = Column(JSON)
    ultima_atualizacao = Column(DateTime, default=datetime.utcnow, index=True)
    dados_consolidados = Column(JSON)
    observacoes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Funções auxiliares

def format_cnpj(cnpj: str) -> str:
    """Formata CNPJ"""
    clean_cnpj = cnpj.replace(".", "").replace("/", "").replace("-", "")
    return f"{clean_cnpj[:2]}.{clean_cnpj[2:5]}.{clean_cnpj[5:8]}/{clean_cnpj[8:12]}-{clean_cnpj[12:14]}"


def create_tables():
    """Cria as tabelas no banco de dados"""
    Base.metadata.create_all(bind=engine)


def get_cliente_by_cnpj(db: Session, cnpj: str) -> Cliente:
    """Busca cliente por CNPJ"""
    return db.query(Cliente).filter(Cliente.cnpj == cnpj).first()


def create_cliente(db: Session, cliente_data: dict) -> Cliente:
    """Cria novo cliente"""
    cliente = Cliente(**cliente_data)
    db.add(cliente)
    db.commit()
    db.refresh(cliente)
    return cliente


def update_cliente(db: Session, cnpj: str, cliente_data: dict) -> Cliente:
    """Atualiza cliente existente"""
    cliente = get_cliente_by_cnpj(db, cnpj)
    if cliente:
        for key, value in cliente_data.items():
            setattr(cliente, key, value)
        cliente.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(cliente)
    return cliente


def create_consulta_log(db: Session, log_data: dict) -> ConsultaLog:
    """Cria log de consulta"""
    log = ConsultaLog(**log_data)
    db.add(log)
    db.commit()
    db.refresh(log)
    return log 