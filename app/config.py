from pydantic import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # Database
    database_url: str = "sqlite:///./bot_ecac.db"
    
    # SERPRO Integra Contador
    serpro_consumer_key: str
    serpro_consumer_secret: str
    serpro_base_url: str = "https://gateway.apiserpro.serpro.gov.br/integra-contador/v1"
    serpro_token_url: str = "https://gateway.apiserpro.serpro.gov.br/token"
    serpro_ambiente: str = "producao"  # producao ou homologacao
    
    # Certificado Digital
    certificado_path: str = "./certs/certificado.pfx"
    certificado_senha: str
    cpf_procurador: str
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_debug: bool = False
    
    # Cache e Performance
    token_cache_minutes: int = 55  # Margem de 5 min do token de 1h
    request_timeout_seconds: int = 30
    max_retries: int = 3
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "./logs/bot_ecac.log"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignorar campos extras do .env


# URLs baseadas no ambiente
def get_serpro_urls(ambiente: str = "homologacao"):
    """Retorna URLs baseadas no ambiente"""
    if ambiente == "homologacao":
        return {
            "base_url": "https://gateway.apiserpro.serpro.gov.br/integra-contador/v1",
            "token_url": "https://gateway.apiserpro.serpro.gov.br/token"
        }
    else:
        return {
            "base_url": "https://gateway.serpro.gov.br/integra-contador/v1", 
            "token_url": "https://gateway.serpro.gov.br/token"
        }


# Instância global das configurações
settings = Settings() 