import httpx
import asyncio
import base64
import ssl
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from loguru import logger

from app.config import settings, get_serpro_urls
from app.token_cache import token_cache


class SerproClient:
    """Cliente simplificado para APIs SERPRO Integra Contador"""
    
    def __init__(self):
        self.consumer_key = settings.serpro_consumer_key
        self.consumer_secret = settings.serpro_consumer_secret
        self.cpf_procurador = settings.cpf_procurador
        
        # URLs baseadas no ambiente
        urls = get_serpro_urls(settings.serpro_ambiente)
        self.base_url = urls["base_url"]
        self.token_url = urls["token_url"]
        
        # SSL Context para certificado
        self.ssl_context = self._setup_ssl()
        
    def _setup_ssl(self) -> ssl.SSLContext:
        """Configura contexto SSL com certificado digital"""
        try:
            cert_path = Path(settings.certificado_path)
            
            if cert_path.exists() and cert_path.suffix.lower() == '.pfx':
                logger.info(f"Certificado PFX encontrado: {cert_path}")
                # Para PFX, usar contexto padrão por enquanto
                context = ssl.create_default_context()
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                return context
            elif cert_path.exists() and cert_path.suffix.lower() in ['.pem', '.crt']:
                logger.info(f"Certificado PEM encontrado: {cert_path}")
                context = ssl.create_default_context()
                context.load_cert_chain(cert_path)
                return context
            else:
                logger.warning("Certificado não encontrado, usando SSL padrão")
                return ssl.create_default_context()
                
        except Exception as e:
            logger.error(f"Erro ao configurar SSL: {e}")
            return ssl.create_default_context()
    
    async def _get_oauth_token(self) -> str:
        """Obtém token OAuth2 do SERPRO"""
        try:
            logger.info("Obtendo novo token OAuth2...")
            
            # Verificar cache primeiro
            cached_token = token_cache.get_token()
            if cached_token:
                return cached_token
            
            # Preparar credenciais
            credentials = base64.b64encode(
                f"{self.consumer_key}:{self.consumer_secret}".encode()
            ).decode()
            
            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "BotECAC/1.0"
            }
            
            data = "grant_type=client_credentials"
            
            async with httpx.AsyncClient(
                timeout=settings.request_timeout_seconds,
                verify=self.ssl_context
            ) as client:
                response = await client.post(
                    self.token_url,
                    headers=headers,
                    content=data
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    access_token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    
                    # Salvar no cache
                    token_cache.save_token(access_token, expires_in)
                    
                    logger.success("Token OAuth2 obtido com sucesso")
                    return access_token
                else:
                    logger.error(f"Erro ao obter token: {response.status_code} - {response.text}")
                    raise Exception(f"Erro OAuth2: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Erro ao obter token OAuth2: {e}")
            raise
    
    async def _make_request(self, endpoint: str) -> Dict[str, Any]:
        """Faz requisição para API do SERPRO"""
        max_retries = settings.max_retries
        
        for attempt in range(max_retries):
            try:
                token = await self._get_oauth_token()
                url = f"{self.base_url}{endpoint}"
                
                headers = {
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                    "User-Agent": "BotECAC/1.0",
                    "X-CPF-Procurador": self.cpf_procurador
                }
                
                logger.info(f"Tentativa {attempt + 1}: GET {url}")
                
                async with httpx.AsyncClient(
                    timeout=settings.request_timeout_seconds,
                    verify=self.ssl_context
                ) as client:
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        logger.success(f"Consulta bem-sucedida: {endpoint}")
                        return response.json()
                    elif response.status_code == 404:
                        logger.warning(f"📋 API não encontrada: {endpoint} - Verifique se tem acesso ou se a procuração está válida")
                        return {"status": "not_found", "error": "API não encontrada ou sem acesso", "data": None}
                    elif response.status_code == 403:
                        logger.error(f"🚫 ACESSO NEGADO: {endpoint} - Procuração pode estar EXPIRADA!")
                        return {"status": "forbidden", "error": "Acesso negado - Procuração expirada", "data": None}
                    elif response.status_code == 401:
                        logger.warning("Token inválido, limpando cache...")
                        token_cache.clear()
                        if attempt < max_retries - 1:
                            continue
                        raise Exception("Erro de autenticação")
                    else:
                        logger.error(f"Erro API: {response.status_code} - {response.text}")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(2 ** attempt)  # Exponential backoff
                            continue
                        raise Exception(f"Erro API: {response.status_code}")
                        
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Tentativa {attempt + 1} falhou: {e}, tentando novamente...")
                    await asyncio.sleep(2 ** attempt)
                else:
                    logger.error(f"Todas as tentativas falharam para {endpoint}: {e}")
                    raise
        
        raise Exception(f"Máximo de tentativas excedido para {endpoint}")
    
    # Métodos de consulta específicos
    async def consultar_pgmei_divida_ativa(self, cnpj: str) -> Dict[str, Any]:
        """Consulta dívida ativa no PGMEI"""
        return await self._make_request(f"/pgmei/divida-ativa/{cnpj}")
    
    async def consultar_pgdasd_declaracoes(self, cnpj: str) -> Dict[str, Any]:
        """Consulta declarações no PGDASD"""
        return await self._make_request(f"/pgdasd/declaracoes/{cnpj}")
    
    async def consultar_ccmei_dados(self, cnpj: str) -> Dict[str, Any]:
        """Consulta dados do CCMEI"""
        return await self._make_request(f"/ccmei/dados/{cnpj}")
    
    async def consultar_ccmei_situacao_cadastral(self, cnpj: str) -> Dict[str, Any]:
        """Consulta situação cadastral no CCMEI"""
        return await self._make_request(f"/ccmei/situacao-cadastral/{cnpj}")
    
    async def consultar_caixa_postal(self, cnpj: str) -> Dict[str, Any]:
        """Consulta mensagens do caixa postal"""
        return await self._make_request(f"/caixa-postal/mensagens/{cnpj}")
    
    async def consultar_procuracoes(self, cnpj: str) -> Dict[str, Any]:
        """Consulta procurações ativas"""
        return await self._make_request(f"/procuracoes/{cnpj}")
    
    async def consultar_todas_apis(self, cnpj: str) -> Dict[str, Dict[str, Any]]:
        """Consulta todas as APIs em paralelo"""
        logger.info(f"Iniciando consulta completa para CNPJ: {cnpj}")
        
        # Executar todas as consultas em paralelo
        tasks = {
            "pgmei_divida": self.consultar_pgmei_divida_ativa(cnpj),
            "pgdasd_declaracoes": self.consultar_pgdasd_declaracoes(cnpj),
            "ccmei_dados": self.consultar_ccmei_dados(cnpj),
            "ccmei_situacao": self.consultar_ccmei_situacao_cadastral(cnpj),
            "caixa_postal": self.consultar_caixa_postal(cnpj),
            "procuracoes": self.consultar_procuracoes(cnpj)
        }
        
        resultados = {}
        for nome, task in tasks.items():
            try:
                resultados[nome] = await task
                logger.info(f"✅ {nome}: OK")
            except Exception as e:
                logger.error(f"❌ {nome}: {e}")
                resultados[nome] = {"status": "error", "error": str(e)}
        
        logger.success(f"Consulta completa finalizada para CNPJ: {cnpj}")
        return resultados


# Instância global do cliente
serpro_client = SerproClient() 