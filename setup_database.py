#!/usr/bin/env python3
"""
Script para criar a estrutura do banco Bot e-CAC no PostgreSQL remoto
Servidor: 161.35.141.62:9000
Banco: n8n_usenodes
"""

import psycopg2
import sys
from datetime import datetime

# Configurações de conexão
DB_CONFIG = {
    'host': '161.35.141.62',
    'port': 9000,
    'database': 'n8n_usenodes',
    'user': 'postgres',
    'password': '3ad3550763e84d5864a7'
}

def conectar_postgres():
    """Conecta ao PostgreSQL remoto"""
    try:
        print(f"🔌 Conectando ao PostgreSQL...")
        print(f"   Host: {DB_CONFIG['host']}:{DB_CONFIG['port']}")
        print(f"   Banco: {DB_CONFIG['database']}")
        print(f"   Usuário: {DB_CONFIG['user']}")
        
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Conectado com sucesso!")
        return conn
    
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def executar_sql_arquivo(cursor, arquivo_sql):
    """Executa o arquivo SQL"""
    try:
        print(f"📂 Lendo arquivo: {arquivo_sql}")
        
        with open(arquivo_sql, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        print(f"📊 Executando SQL ({len(sql_content)} caracteres)...")
        
        # Executar SQL
        cursor.execute(sql_content)
        
        print("✅ SQL executado com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao executar SQL: {e}")
        return False

def verificar_tabelas(cursor):
    """Verifica se as tabelas foram criadas"""
    try:
        print("🔍 Verificando tabelas criadas...")
        
        cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN (
                'clientes', 'consultas_log', 'dividas_ativas', 
                'declaracoes', 'guias_mei', 'caixa_postal',
                'parcelamentos', 'procuracoes', 'configuracoes', 'haylander'
            )
            ORDER BY table_name;
        """)
        
        tabelas = cursor.fetchall()
        
        print(f"\n📋 TABELAS CRIADAS ({len(tabelas)}/10):")
        for nome, tipo in tabelas:
            print(f"   ✅ {nome} ({tipo})")
        
        # Verificar configurações inseridas
        cursor.execute("SELECT COUNT(*) FROM configuracoes;")
        count_config = cursor.fetchone()[0]
        print(f"\n⚙️  CONFIGURAÇÕES: {count_config} registros inseridos")
        
        if len(tabelas) == 10:
            print("\n🎉 ESTRUTURA DO BANCO CRIADA COM SUCESSO!")
            return True
        else:
            print(f"\n⚠️  Algumas tabelas não foram criadas. Esperado: 10, Encontrado: {len(tabelas)}")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar tabelas: {e}")
        return False

def main():
    """Função principal"""
    print("=" * 60)
    print("🚀 BOT E-CAC - SETUP DO BANCO DE DADOS")
    print("=" * 60)
    print(f"⏰ Iniciado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Conectar ao banco
    conn = conectar_postgres()
    if not conn:
        print("❌ Não foi possível conectar ao banco!")
        sys.exit(1)
    
    try:
        cursor = conn.cursor()
        
        # Executar SQL
        if executar_sql_arquivo(cursor, 'database_setup.sql'):
            # Confirmar transação
            conn.commit()
            print("💾 Transação confirmada!")
            
            # Verificar resultado
            verificar_tabelas(cursor)
            
        else:
            print("❌ Erro ao executar SQL. Fazendo rollback...")
            conn.rollback()
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        conn.rollback()
        
    finally:
        cursor.close()
        conn.close()
        print("\n🔌 Conexão fechada.")
        print("=" * 60)

if __name__ == "__main__":
    main() 