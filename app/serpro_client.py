"""
Cliente para integração com SERPRO Integra Contador
"""

import httpx
import asyncio
import json
import base64
import ssl
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from loguru import logger
from app.config import get_settings

settings = get_settings()


class SerproClient:
    """Cliente para comunicação com SERPRO Integra Contador"""
    
    def __init__(self):
        self.base_url = settings.serpro_base_url
        self.token_url = settings.serpro_token_url
        self.consumer_key = settings.serpro_consumer_key
        self.consumer_secret = settings.serpro_consumer_secret
        self.certificado_path = settings.certificado_path
        self.certificado_senha = settings.certificado_senha
        self.cpf_procurador = settings.cpf_procurador.replace(".", "").replace("-", "")
        
        # Cache do token
        self._token = None
        self._token_expires = None
        
        # Configurar SSL context para certificado
        self._ssl_context = self._create_ssl_context()
    
    def _create_ssl_context(self) -> ssl.SSLContext:
        """Cria contexto SSL com certificado digital"""
        try:
            context = ssl.create_default_context()
            
            # Carregar certificado se existir
            try:
                context.load_cert_chain(
                    self.certificado_path, 
                    password=self.certificado_senha
                )
                logger.info(f"Certificado carregado: {self.certificado_path}")
            except Exception as e:
                logger.warning(f"Erro ao carregar certificado: {e}")
                logger.info("Continuando sem certificado digital")
            
            return context
            
        except Exception as e:
            logger.error(f"Erro ao criar contexto SSL: {e}")
            return ssl.create_default_context()
    
    async def _get_oauth_token(self) -> str:
        """Obtém token OAuth2 do SERPRO"""
        try:
            logger.info("Obtendo token OAuth2 do SERPRO...")
            
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
                verify=self._ssl_context
            ) as client:
                response = await client.post(
                    self.token_url,
                    headers=headers,
                    data=data
                )
                
                if response.status_code == 200:
                    token_data = response.json()
                    token = token_data["access_token"]
                    expires_in = token_data.get("expires_in", 3600)
                    
                    # Cache do token
                    self._token = token
                    self._token_expires = datetime.now() + timedelta(
                        seconds=expires_in - 60  # 1 minuto de margem
                    )
                    
                    logger.info("Token OAuth2 obtido com sucesso")
                    return token
                    
                else:
                    logger.error(f"Erro ao obter token: {response.status_code} - {response.text}")
                    raise Exception(f"Erro ao obter token OAuth2: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Erro ao obter token OAuth2: {e}")
            raise
    
    async def get_token(self) -> str:
        """Retorna token válido (usa cache se disponível)"""
        if self._token and self._token_expires and datetime.now() < self._token_expires:
            return self._token
        
        return await self._get_oauth_token()
    
    async def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> Dict[str, Any]:
        """Faz requisição para API do SERPRO"""
        try:
            token = await self.get_token()
            url = f"{self.base_url}{endpoint}"
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "BotECAC/1.0",
                "X-CPF-Procurador": self.cpf_procurador
            }
            
            # Atualizar headers com os fornecidos
            if "headers" in kwargs:
                headers.update(kwargs.pop("headers"))
            
            logger.info(f"Fazendo requisição: {method} {url}")
            
            async with httpx.AsyncClient(
                timeout=settings.request_timeout_seconds,
                verify=self._ssl_context
            ) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=headers,
                    **kwargs
                )
                
                logger.info(f"Status response: {response.status_code}")
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 401:
                    # Token expirado, tentar renovar
                    logger.warning("Token expirado, renovando...")
                    self._token = None
                    self._token_expires = None
                    
                    # Tentar novamente com novo token
                    token = await self.get_token()
                    headers["Authorization"] = f"Bearer {token}"
                    
                    response = await client.request(
                        method=method,
                        url=url,
                        headers=headers,
                        **kwargs
                    )
                    
                    if response.status_code == 200:
                        return response.json()
                    else:
                        raise Exception(f"Erro após renovar token: {response.status_code} - {response.text}")
                        
                else:
                    error_text = response.text
                    logger.error(f"Erro na requisição: {response.status_code} - {error_text}")
                    raise Exception(f"Erro na API SERPRO: {response.status_code} - {error_text}")
                    
        except Exception as e:
            logger.error(f"Erro na requisição SERPRO: {e}")
            raise
    
    async def consultar_pgmei_divida_ativa(self, cnpj: str) -> Dict[str, Any]:
        """Consulta dívida ativa no PGMEI"""
        endpoint = f"/pgmei/divida-ativa/{cnpj}"
        return await self._make_request("GET", endpoint)
    
    async def consultar_pgdasd_declaracoes(self, cnpj: str, ano: Optional[int] = None) -> Dict[str, Any]:
        """Consulta declarações no PGDASD"""
        endpoint = f"/pgdasd/declaracoes/{cnpj}"
        if ano:
            endpoint += f"?ano={ano}"
        return await self._make_request("GET", endpoint)
    
    async def consultar_ccmei_dados(self, cnpj: str) -> Dict[str, Any]:
        """Consulta dados do CCMEI"""
        endpoint = f"/ccmei/dados/{cnpj}"
        return await self._make_request("GET", endpoint)
    
    async def consultar_ccmei_situacao_cadastral(self, cnpj: str) -> Dict[str, Any]:
        """Consulta situação cadastral no CCMEI"""
        endpoint = f"/ccmei/situacao-cadastral/{cnpj}"
        return await self._make_request("GET", endpoint)
    
    async def consultar_caixa_postal(self, cnpj: str) -> Dict[str, Any]:
        """Consulta caixa postal"""
        endpoint = f"/caixa-postal/mensagens/{cnpj}"
        return await self._make_request("GET", endpoint)
    
    async def consultar_procuracoes(self, cnpj: str) -> Dict[str, Any]:
        """Consulta procurações válidas"""
        endpoint = f"/procuracoes/{cnpj}"
        return await self._make_request("GET", endpoint)
    
    async def consultar_parcelamentos_mei(self, cnpj: str) -> Dict[str, Any]:
        """Consulta parcelamentos MEI"""
        endpoint = f"/parcmei/pedidos/{cnpj}"
        return await self._make_request("GET", endpoint)
    
    async def consultar_parcelamentos_simples(self, cnpj: str) -> Dict[str, Any]:
        """Consulta parcelamentos Simples Nacional"""
        endpoint = f"/parcsn/pedidos/{cnpj}"
        return await self._make_request("GET", endpoint)
    
    async def consultar_todas_informacoes(self, cnpj: str) -> Dict[str, Any]:
        """Consulta todas as informações de um CNPJ"""
        logger.info(f"Iniciando consulta completa para CNPJ: {cnpj}")
        
        resultados = {
            "cnpj": cnpj,
            "timestamp": datetime.now().isoformat(),
            "consultas": {}
        }
        
        # Lista de consultas a serem feitas
        consultas = [
            ("pgmei_divida_ativa", self.consultar_pgmei_divida_ativa),
            ("pgdasd_declaracoes", self.consultar_pgdasd_declaracoes),
            ("ccmei_dados", self.consultar_ccmei_dados),
            ("ccmei_situacao", self.consultar_ccmei_situacao_cadastral),
            ("caixa_postal", self.consultar_caixa_postal),
            ("procuracoes", self.consultar_procuracoes),
            ("parcelamentos_mei", self.consultar_parcelamentos_mei),
            ("parcelamentos_simples", self.consultar_parcelamentos_simples),
        ]
        
        # Executar consultas
        for nome, funcao in consultas:
            try:
                logger.info(f"Consultando {nome}...")
                resultado = await funcao(cnpj)
                resultados["consultas"][nome] = {
                    "success": True,
                    "data": resultado
                }
                logger.info(f"Consulta {nome} concluída com sucesso")
                
            except Exception as e:
                logger.error(f"Erro na consulta {nome}: {e}")
                resultados["consultas"][nome] = {
                    "success": False,
                    "error": str(e)
                }
                
            # Pequena pausa entre requisições
            await asyncio.sleep(0.5)
        
        logger.info(f"Consulta completa finalizada para CNPJ: {cnpj}")
        return resultados
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica se a API está funcionando"""
        try:
            token = await self.get_token()
            return {
                "status": "connected",
                "token_obtido": True,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "token_obtido": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Instância global do cliente
serpro_client = SerproClient()


def get_serpro_client() -> SerproClient:
    """Retorna instância do cliente SERPRO"""
    return serpro_client 