"""
Configurações da aplicação Bot e-CAC
"""

import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from app.constants import *


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # API
    api_title: str = API_TITLE
    api_description: str = API_DESCRIPTION
    api_version: str = API_VERSION
    api_host: str = "0.0.0.0"
    api_port: int = API_PORT
    api_debug: bool = False
    
    # Database
    database_url: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    db_host: str = DB_HOST
    db_port: int = DB_PORT
    db_user: str = DB_USER
    db_password: str = DB_PASSWORD
    db_name: str = DB_NAME
    db_schema: str = DB_SCHEMA
    
    # SERPRO Integra Contador
    serpro_consumer_key: str = SERPRO_CONSUMER_KEY
    serpro_consumer_secret: str = SERPRO_CONSUMER_SECRET
    serpro_base_url: str = SERPRO_BASE_URL
    serpro_token_url: str = SERPRO_TOKEN_URL
    serpro_ambiente: str = SERPRO_AMBIENTE
    
    # Certificado Digital
    certificado_path: str = CERTIFICADO_PATH
    certificado_senha: str = CERTIFICADO_SENHA
    cpf_procurador: str = CPF_PROCURADOR
    
    # Segurança
    secret_key: str = Field(default="sua_secret_key_super_secreta_aqui", env="SECRET_KEY")
    jwt_secret: str = Field(default="seu_jwt_secret_aqui", env="JWT_SECRET")
    api_token_bearer: Optional[str] = Field(default=None, env="API_TOKEN_BEARER")
    
    # Logs
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    log_file: str = Field(default="./logs/bot_ecac.log", env="LOG_FILE")
    
    # Cache e Performance
    token_cache_minutes: int = Field(default=55, env="TOKEN_CACHE_MINUTES")
    request_timeout_seconds: int = Field(default=30, env="REQUEST_TIMEOUT_SECONDS")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    # CORS
    cors_origins: List[str] = Field(default=["*"], env="CORS_ORIGINS")
    cors_methods: List[str] = Field(default=["GET", "POST", "PUT", "DELETE"], env="CORS_METHODS")
    
    # Dados de teste
    cnpj_teste: str = Field(default="49189181000135", env="CNPJ_TESTE")
    razao_social_teste: str = Field(default="Gustavo Souza de Oliveira", env="RAZAO_SOCIAL_TESTE")
    
    # Monitoramento
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    health_check_interval: int = Field(default=60, env="HEALTH_CHECK_INTERVAL")
    
    class Config:
        env_file = "config.env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Instância global das configurações
settings = Settings()


def get_settings() -> Settings:
    """Retorna as configurações da aplicação"""
    return settings 