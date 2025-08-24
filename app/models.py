from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.database import Base


class Haylander(Base):
    """Modelo para dados consolidados dos clientes"""
    
    __tablename__ = "haylander"
    
    # Identificação
    id = Column(Integer, primary_key=True, index=True)
    cnpj = Column(String(14), unique=True, index=True, nullable=False)
    razao_social = Column(String(255))
    
    # PGMEI - Dívida Ativa
    pgmei_divida_valor = Column(DECIMAL(15, 2), default=0.00)
    pgmei_tem_divida = Column(Boolean, default=False)
    pgmei_ultimo_update = Column(DateTime)
    
    # PGDASD - Declarações
    pgdasd_pendentes_count = Column(Integer, default=0)
    pgdasd_anos_pendentes = Column(Text)  # "2022,2023,2024"
    pgdasd_ultimo_update = Column(DateTime)
    
    # CCMEI - Dados Cadastrais
    ccmei_situacao = Column(String(100))
    ccmei_data_abertura = Column(DateTime)
    ccmei_ultimo_update = Column(DateTime)
    
    # Caixa Postal
    caixa_mensagens_count = Column(Integer, default=0)
    caixa_mensagens_nao_lidas = Column(Integer, default=0)
    caixa_ultimo_update = Column(DateTime)
    
    # Procurações
    procuracoes_ativas = Column(Integer, default=0)
    procuracoes_ultimo_update = Column(DateTime)
    
    # Consolidação Simples
    situacao_geral = Column(String(50))  # "OK", "PENDENCIAS", "PROBLEMAS"
    valor_total_pendente = Column(DECIMAL(15, 2), default=0.00)
    ultima_consulta = Column(DateTime)
    status_consulta = Column(String(20))  # "SUCCESS", "ERROR"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<Haylander(cnpj={self.cnpj}, razao_social={self.razao_social})>" 