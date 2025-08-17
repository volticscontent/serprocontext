-- =====================================================
-- BOT E-CAC - ESTRUTURA COMPLETA DO BANCO DE DADOS
-- Banco: n8n_usenodes
-- Servidor: 161.35.141.62:9000
-- =====================================================

-- Configurar schema se necessário
SET search_path TO public;

-- =====================================================
-- 1. TABELA: consultas_log (Histórico de consultas)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.consultas_log (
    id SERIAL PRIMARY KEY,
    request_id VARCHAR(50) UNIQUE NOT NULL,
    cnpj VARCHAR(14) NOT NULL,
    razao_social VARCHAR(255),
    nome_cliente VARCHAR(255),
    telefone VARCHAR(20),
    data_consulta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'SUCCESS', -- SUCCESS, ERROR, PENDING
    tempo_resposta_ms INTEGER,
    ip_origem INET,
    user_agent TEXT,
    dados_request JSONB,
    dados_response JSONB,
    errors_log JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 2. TABELA: clientes (Dados dos clientes)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.clientes (
    id SERIAL PRIMARY KEY,
    cnpj VARCHAR(14) UNIQUE NOT NULL,
    cnpj_formatado VARCHAR(18),
    razao_social VARCHAR(255) NOT NULL,
    nome_fantasia VARCHAR(255),
    is_mei BOOLEAN DEFAULT FALSE,
    situacao VARCHAR(50), -- ATIVO, INATIVO, SUSPENSO
    data_abertura DATE,
    estado VARCHAR(2),
    municipio VARCHAR(100),
    cep VARCHAR(10),
    atividade_principal_codigo VARCHAR(20),
    atividade_principal_descricao TEXT,
    email VARCHAR(255),
    telefone VARCHAR(20),
    status_geral VARCHAR(50), -- OK, PENDENCIAS, IRREGULAR
    ultima_consulta TIMESTAMP,
    dados_completos JSONB, -- JSON com todos os dados
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 3. TABELA: dividas_ativas (Dívidas encontradas)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.dividas_ativas (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE,
    cnpj VARCHAR(14) NOT NULL,
    tipo_divida VARCHAR(20), -- UNIAO, ESTADO, MUNICIPIO, MEI
    numero_inscricao VARCHAR(50),
    periodo VARCHAR(10), -- YYYY-MM
    valor_principal DECIMAL(15,2) DEFAULT 0.00,
    valor_multa DECIMAL(15,2) DEFAULT 0.00,
    valor_juros DECIMAL(15,2) DEFAULT 0.00,
    valor_total DECIMAL(15,2) DEFAULT 0.00,
    situacao VARCHAR(20), -- ATIVA, PAGA, PARCELADA
    data_vencimento DATE,
    data_inclusao DATE,
    origem VARCHAR(50), -- PGMEI, PGDASD, OUTROS
    dados_completos JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 4. TABELA: declaracoes (PGDASD, MEI, DCTFWEB)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.declaracoes (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE,
    cnpj VARCHAR(14) NOT NULL,
    tipo VARCHAR(20), -- PGDASD, MEI, DCTFWEB, DEFIS
    periodo VARCHAR(10), -- YYYY-MM
    ano INTEGER,
    situacao VARCHAR(30), -- TRANSMITIDA, PENDENTE, RETIFICADA, PROCESSADA
    data_transmissao TIMESTAMP,
    data_vencimento DATE,
    recibo VARCHAR(50),
    valor_devido DECIMAL(15,2) DEFAULT 0.00,
    valor_pago DECIMAL(15,2) DEFAULT 0.00,
    em_atraso BOOLEAN DEFAULT FALSE,
    dados_declaracao JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 5. TABELA: guias_mei (Guias DAS MEI)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.guias_mei (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE,
    cnpj VARCHAR(14) NOT NULL,
    periodo VARCHAR(10), -- YYYY-MM
    tipo_guia VARCHAR(20), -- DAS_MEI, DAS_SIMPLES
    codigo_barras VARCHAR(48),
    linha_digitavel VARCHAR(48),
    valor DECIMAL(10,2) NOT NULL,
    data_vencimento DATE,
    data_pagamento DATE,
    situacao VARCHAR(20), -- PENDENTE, PAGO, VENCIDO
    pdf_base64 TEXT,
    dados_completos JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 6. TABELA: caixa_postal (Mensagens e-CAC)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.caixa_postal (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE,
    cnpj VARCHAR(14) NOT NULL,
    id_mensagem VARCHAR(50) UNIQUE NOT NULL,
    assunto VARCHAR(500),
    remetente VARCHAR(255),
    conteudo TEXT,
    data_envio TIMESTAMP,
    status VARCHAR(20), -- LIDA, NAO_LIDA
    prioridade VARCHAR(10), -- ALTA, MEDIA, BAIXA
    tem_anexo BOOLEAN DEFAULT FALSE,
    prazo_resposta DATE,
    categoria VARCHAR(50), -- INTIMACAO, NOTIFICACAO, INFORMATIVO
    dados_anexos JSONB,
    dados_completos JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 7. TABELA: parcelamentos (Parcelamentos SERPRO)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.parcelamentos (
    id SERIAL PRIMARY KEY,
    cliente_id INTEGER REFERENCES clientes(id) ON DELETE CASCADE,
    cnpj VARCHAR(14) NOT NULL,
    numero_parcelamento VARCHAR(50) UNIQUE NOT NULL,
    tipo VARCHAR(20), -- PARCSN, PARCMEI, PERTSN, RELPSN
    situacao VARCHAR(20), -- ATIVO, QUITADO, CANCELADO
    valor_total DECIMAL(15,2),
    quantidade_parcelas INTEGER,
    parcelas_pagas INTEGER DEFAULT 0,
    data_primeira_parcela DATE,
    dados_parcelas JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 8. TABELA: procuracoes (Procurações e-CAC)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.procuracoes (
    id SERIAL PRIMARY KEY,
    cnpj VARCHAR(14) NOT NULL,
    cpf_procurador VARCHAR(11) NOT NULL,
    nome_procurador VARCHAR(255),
    servicos_autorizados JSONB,
    data_inicio DATE,
    data_fim DATE,
    ativa BOOLEAN DEFAULT TRUE,
    dados_completos JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 9. TABELA: configuracoes (Settings da API)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.configuracoes (
    id SERIAL PRIMARY KEY,
    chave VARCHAR(100) UNIQUE NOT NULL,
    valor TEXT,
    descricao TEXT,
    tipo VARCHAR(20), -- STRING, INTEGER, BOOLEAN, JSON
    categoria VARCHAR(50), -- API, SISTEMA, SERPRO
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- 10. TABELA ESPECIAL: haylander (Conforme solicitado)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.haylander (
    id SERIAL PRIMARY KEY,
    cnpj VARCHAR(14) UNIQUE NOT NULL,
    razao_social VARCHAR(255) NOT NULL,
    situacao_mei VARCHAR(50),
    valor_dividas DECIMAL(15,2) DEFAULT 0.00,
    declaracoes_pendentes JSONB,
    ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    dados_consolidados JSONB,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Clientes
CREATE INDEX IF NOT EXISTS idx_clientes_cnpj ON clientes(cnpj);
CREATE INDEX IF NOT EXISTS idx_clientes_situacao ON clientes(situacao);

-- Consultas Log
CREATE INDEX IF NOT EXISTS idx_consultas_log_cnpj ON consultas_log(cnpj);
CREATE INDEX IF NOT EXISTS idx_consultas_log_data ON consultas_log(data_consulta);
CREATE INDEX IF NOT EXISTS idx_consultas_log_status ON consultas_log(status);

-- Dívidas Ativas
CREATE INDEX IF NOT EXISTS idx_dividas_ativas_cnpj ON dividas_ativas(cnpj);
CREATE INDEX IF NOT EXISTS idx_dividas_ativas_tipo ON dividas_ativas(tipo_divida);
CREATE INDEX IF NOT EXISTS idx_dividas_ativas_situacao ON dividas_ativas(situacao);

-- Declarações
CREATE INDEX IF NOT EXISTS idx_declaracoes_cnpj_periodo ON declaracoes(cnpj, periodo);
CREATE INDEX IF NOT EXISTS idx_declaracoes_tipo ON declaracoes(tipo);
CREATE INDEX IF NOT EXISTS idx_declaracoes_situacao ON declaracoes(situacao);

-- Caixa Postal
CREATE INDEX IF NOT EXISTS idx_caixa_postal_cnpj_status ON caixa_postal(cnpj, status);
CREATE INDEX IF NOT EXISTS idx_caixa_postal_data_envio ON caixa_postal(data_envio);

-- Haylander
CREATE INDEX IF NOT EXISTS idx_haylander_cnpj ON haylander(cnpj);
CREATE INDEX IF NOT EXISTS idx_haylander_ultima_atualizacao ON haylander(ultima_atualizacao);

-- =====================================================
-- FUNÇÃO PARA UPDATE AUTOMÁTICO DE updated_at
-- =====================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- =====================================================
-- TRIGGERS PARA TODAS AS TABELAS
-- =====================================================
DROP TRIGGER IF EXISTS update_clientes_updated_at ON clientes;
CREATE TRIGGER update_clientes_updated_at 
    BEFORE UPDATE ON clientes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_consultas_log_updated_at ON consultas_log;
CREATE TRIGGER update_consultas_log_updated_at 
    BEFORE UPDATE ON consultas_log 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_dividas_ativas_updated_at ON dividas_ativas;
CREATE TRIGGER update_dividas_ativas_updated_at 
    BEFORE UPDATE ON dividas_ativas 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_declaracoes_updated_at ON declaracoes;
CREATE TRIGGER update_declaracoes_updated_at 
    BEFORE UPDATE ON declaracoes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_guias_mei_updated_at ON guias_mei;
CREATE TRIGGER update_guias_mei_updated_at 
    BEFORE UPDATE ON guias_mei 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_caixa_postal_updated_at ON caixa_postal;
CREATE TRIGGER update_caixa_postal_updated_at 
    BEFORE UPDATE ON caixa_postal 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_parcelamentos_updated_at ON parcelamentos;
CREATE TRIGGER update_parcelamentos_updated_at 
    BEFORE UPDATE ON parcelamentos 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_procuracoes_updated_at ON procuracoes;
CREATE TRIGGER update_procuracoes_updated_at 
    BEFORE UPDATE ON procuracoes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_configuracoes_updated_at ON configuracoes;
CREATE TRIGGER update_configuracoes_updated_at 
    BEFORE UPDATE ON configuracoes 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_haylander_updated_at ON haylander;
CREATE TRIGGER update_haylander_updated_at 
    BEFORE UPDATE ON haylander 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- INSERIR CONFIGURAÇÕES INICIAIS
-- =====================================================
INSERT INTO configuracoes (chave, valor, descricao, tipo, categoria) VALUES
('serpro_consumer_key', 'fddUi1Ks7TjsQQ0skrT7jsA9Onoa', 'Consumer Key do SERPRO', 'STRING', 'SERPRO'),
('serpro_consumer_secret', 'yA6nleyxTV_GlYkDg8xjyrAjh0Qa', 'Consumer Secret do SERPRO', 'STRING', 'SERPRO'),
('serpro_ambiente', 'homologacao', 'Ambiente SERPRO (homologacao/producao)', 'STRING', 'SERPRO'),
('certificado_path', '/app/certs/HAYLANDER MARTINS CONTABILIDADE LTDA51564549000140.pfx', 'Caminho do certificado digital', 'STRING', 'SERPRO'),
('certificado_senha', '300@Martins', 'Senha do certificado digital', 'STRING', 'SERPRO'),
('cpf_procurador', '122.643.046-50', 'CPF do procurador', 'STRING', 'SERPRO'),
('api_version', '1.0.0', 'Versão da API Bot e-CAC', 'STRING', 'API'),
('log_level', 'INFO', 'Nível de log (DEBUG, INFO, WARN, ERROR)', 'STRING', 'SISTEMA'),
('rate_limit_per_minute', '60', 'Limite de requisições por minuto', 'INTEGER', 'API'),
('token_cache_minutes', '55', 'Tempo de cache do token OAuth (minutos)', 'INTEGER', 'SERPRO')
ON CONFLICT (chave) DO NOTHING;

-- =====================================================
-- VIEWS ÚTEIS PARA CONSULTAS (criadas após as tabelas)
-- =====================================================
-- View será criada posteriormente via script separado

-- =====================================================
-- COMENTÁRIOS NAS TABELAS
-- =====================================================
COMMENT ON TABLE clientes IS 'Dados principais dos clientes (empresas/MEI)';
COMMENT ON TABLE consultas_log IS 'Log de todas as consultas realizadas na API';
COMMENT ON TABLE dividas_ativas IS 'Dívidas ativas encontradas (União, Estado, Município)';
COMMENT ON TABLE declaracoes IS 'Declarações fiscais (PGDASD, MEI, DCTFWEB)';
COMMENT ON TABLE guias_mei IS 'Guias DAS MEI geradas';
COMMENT ON TABLE caixa_postal IS 'Mensagens da caixa postal do e-CAC';
COMMENT ON TABLE parcelamentos IS 'Parcelamentos ativos ou quitados';
COMMENT ON TABLE procuracoes IS 'Procurações eletrônicas válidas';
COMMENT ON TABLE configuracoes IS 'Configurações da aplicação';
COMMENT ON TABLE haylander IS 'Tabela específica para dados consolidados do Haylander';

-- =====================================================
-- SUCESSO!
-- =====================================================
SELECT 'BOT E-CAC: Estrutura do banco criada com sucesso!' as status; 