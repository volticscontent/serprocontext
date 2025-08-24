import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional
from loguru import logger


class TokenCache:
    """Cache simples para tokens OAuth em arquivo local"""
    
    def __init__(self, cache_file: str = "token_cache.json"):
        self.cache_file = Path(cache_file)
        
    def get_token(self) -> Optional[str]:
        """Recupera token do cache se ainda válido"""
        try:
            if not self.cache_file.exists():
                return None
            
            data = json.loads(self.cache_file.read_text(encoding="utf-8"))
            
            # Verificar se ainda é válido (margem de 5 minutos)
            expires_at = datetime.fromisoformat(data["expires_at"])
            if datetime.now() + timedelta(minutes=5) >= expires_at:
                logger.info("Token expirado no cache, removendo...")
                self._clear_cache()
                return None
                
            logger.info("Token válido encontrado no cache")
            return data["token"]
            
        except Exception as e:
            logger.warning(f"Erro ao ler cache de token: {e}")
            self._clear_cache()
            return None
    
    def save_token(self, token: str, expires_in: int):
        """Salva token no cache com expiração"""
        try:
            expires_at = datetime.now() + timedelta(seconds=expires_in)
            
            data = {
                "token": token,
                "expires_at": expires_at.isoformat(),
                "created_at": datetime.now().isoformat()
            }
            
            # Criar diretório se não existir
            self.cache_file.parent.mkdir(parents=True, exist_ok=True)
            
            self.cache_file.write_text(json.dumps(data, indent=2), encoding="utf-8")
            logger.info(f"Token salvo no cache, expira em: {expires_at}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar token no cache: {e}")
    
    def _clear_cache(self):
        """Remove arquivo de cache"""
        try:
            if self.cache_file.exists():
                self.cache_file.unlink()
                logger.info("Cache de token limpo")
        except Exception as e:
            logger.error(f"Erro ao limpar cache: {e}")
    
    def clear(self):
        """Método público para limpar cache"""
        self._clear_cache()


# Instância global do cache
token_cache = TokenCache() 