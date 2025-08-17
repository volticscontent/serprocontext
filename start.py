#!/usr/bin/env python3
"""
Script para iniciar a aplicação Bot e-CAC localmente
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        import fastapi
        import uvicorn
        import psycopg2
        print("✅ Dependências principais encontradas")
        return True
    except ImportError as e:
        print(f"❌ Dependência não encontrada: {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def check_certificate():
    """Verifica se o certificado existe"""
    cert_path = "HAYLANDER MARTINS CONTABILIDADE LTDA51564549000140.pfx"
    if os.path.exists(cert_path):
        print(f"✅ Certificado encontrado: {cert_path}")
        return True
    else:
        print(f"⚠️  Certificado não encontrado: {cert_path}")
        print("A aplicação funcionará sem certificado digital")
        return False

def check_config():
    """Verifica se o arquivo de configuração existe"""
    if os.path.exists("config.env"):
        print("✅ Arquivo config.env encontrado")
        return True
    else:
        print("❌ Arquivo config.env não encontrado")
        return False

def create_directories():
    """Cria diretórios necessários"""
    dirs = ["logs", "certs"]
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)
        print(f"✅ Diretório criado/verificado: {dir_name}/")

def main():
    print("🚀 Bot e-CAC API - Inicialização")
    print("=" * 50)
    
    # Verificações
    if not check_config():
        sys.exit(1)
    
    if not check_dependencies():
        sys.exit(1)
    
    create_directories()
    check_certificate()
    
    print("\n🎯 Iniciando servidor...")
    print("📍 URL: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("🔍 Health: http://localhost:8000/health")
    print("\n💡 Para parar: Ctrl+C")
    print("=" * 50)
    
    # Iniciar servidor
    try:
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Servidor parado pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 