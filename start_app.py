#!/usr/bin/env python3
"""
Script para iniciar o Bot e-CAC
"""
import os
import sys
from pathlib import Path

def check_environment():
    """Verifica se o ambiente está configurado corretamente"""
    print("🔍 Verificando ambiente...")
    
    # Verificar .env
    if not Path(".env").exists():
        print("❌ Arquivo .env não encontrado!")
        print("   Execute: cp env.example .env")
        print("   E configure suas credenciais SERPRO")
        return False
    
    # Verificar certificado
    cert_path = Path("./certs/")
    if not cert_path.exists() or not any(cert_path.glob("*.pfx")):
        print("⚠️  Certificado .pfx não encontrado na pasta certs/")
        print("   Certifique-se de colocar seu certificado na pasta certs/")
        return False
    
    print("✅ Ambiente configurado!")
    return True

def main():
    """Função principal"""
    print("🤖 Bot e-CAC - SERPRO Integra Contador")
    print("=" * 50)
    
    if not check_environment():
        sys.exit(1)
    
    print("🚀 Iniciando aplicação...")
    print("📊 Acesse: http://localhost:8000")
    print("📚 Docs: http://localhost:8000/docs")
    print("💖 Health: http://localhost:8000/health")
    print("")
    print("📋 LEMBRE-SE: Verifique se sua procuração SERPRO está válida!")
    print("=" * 50)
    
    # Iniciar aplicação
    os.system("python -m app.main")

if __name__ == "__main__":
    main() 