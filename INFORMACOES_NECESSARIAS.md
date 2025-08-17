# 🤖 BOT E-CAC - INFORMAÇÕES NECESSÁRIAS

Para configurar e implementar seu bot do e-CAC com Integra Contador, preciso das seguintes informações:

## 🔐 1. CREDENCIAIS SERPRO INTEGRA CONTADOR

**OBRIGATÓRIO** - Obtidas no Portal SERPRO após contratação:

- [ ] **Consumer Key**: `_____________________________`
- [ ] **Consumer Secret**: `_____________________________`
- [ ] **Ambiente**: Produção ou Homologação? `_____________________________`

> 📝 **Como obter**: Acesse https://loja.serpro.gov.br/integracontador

---

## 🏢 2. DADOS DA EMPRESA

- [ ] **CNPJ da Empresa**: `_____________________________`
- [ ] **Razão Social**: `_____________________________`
- [ ] **Nome Fantasia**: `_____________________________`
- [ ] **Responsável Técnico**: `_____________________________`
- [ ] **Email Administrativo**: `_____________________________`

---

## 📜 3. CERTIFICADO DIGITAL

**OBRIGATÓRIO** - Para acessar procurações:

- [ ] **Tipo de Certificado**: A1 (arquivo) ou A3 (token/cartão)?
- [ ] **Arquivo do Certificado** (.p12/.pfx): `Enviar arquivo`
- [ ] **Senha do Certificado**: `_____________________________`
- [ ] **Validade do Certificado**: `_____________________________`

---

## 👥 4. CLIENTES E PROCURAÇÕES

**Liste os CNPJs dos clientes que você atende:**

```
Cliente 1:
- CNPJ: _______________
- Nome: _______________
- Serviços: [ ] Simples Nacional [ ] MEI [ ] DCTFWeb [ ] Parcelamentos

Cliente 2:
- CNPJ: _______________
- Nome: _______________
- Serviços: [ ] Simples Nacional [ ] MEI [ ] DCTFWeb [ ] Parcelamentos

Cliente 3:
- CNPJ: _______________
- Nome: _______________
- Serviços: [ ] Simples Nacional [ ] MEI [ ] DCTFWeb [ ] Parcelamentos

[Continue para todos os clientes...]
```

---

## 🗄️ 5. BANCO DE DADOS

**Escolha uma opção:**

### Opção A: PostgreSQL (Recomendado para produção)
- [ ] **Host**: `_____________________________`
- [ ] **Porta**: `_____________________________`
- [ ] **Nome do Banco**: `_____________________________`
- [ ] **Usuário**: `_____________________________`
- [ ] **Senha**: `_____________________________`

### Opção B: SQLite (Para desenvolvimento/teste)
- [ ] **Caminho do arquivo**: `./data/bot_ecac.db` (padrão)

---

## ⚡ 6. REDIS (CACHE)

**Opcional mas recomendado:**

- [ ] **Host**: `_____________________________`
- [ ] **Porta**: `_____________________________`
- [ ] **Senha**: `_____________________________`
- [ ] **Usar Redis?**: [ ] Sim [ ] Não

---

## 📧 7. NOTIFICAÇÕES

### Email (SMTP)
- [ ] **Servidor SMTP**: `_____________________________`
- [ ] **Porta**: `_____________________________`
- [ ] **Usuário**: `_____________________________`
- [ ] **Senha/App Password**: `_____________________________`
- [ ] **Usar TLS?**: [ ] Sim [ ] Não

### Destinatários
- [ ] **Email Administrador**: `_____________________________`
- [ ] **Email para Alertas**: `_____________________________`

### WhatsApp (Opcional)
- [ ] **Usar WhatsApp?**: [ ] Sim [ ] Não
- [ ] **Token da API**: `_____________________________`

### Telegram (Opcional)
- [ ] **Usar Telegram?**: [ ] Sim [ ] Não
- [ ] **Bot Token**: `_____________________________`
- [ ] **Chat ID**: `_____________________________`

---

## ⚙️ 8. CONFIGURAÇÕES OPERACIONAIS

### Intervalos de Verificação
- [ ] **Caixa Postal (minutos)**: `30` (padrão)
- [ ] **Parcelamentos (horas)**: `6` (padrão)
- [ ] **Alertas de Vencimento (dias)**: `7` (padrão)

### Limites e Performance
- [ ] **Máx. Requisições/min**: `60` (padrão)
- [ ] **Requisições Simultâneas**: `10` (padrão)
- [ ] **Timeout Requisição (seg)**: `30` (padrão)

---

## 🖥️ 9. INFRAESTRUTURA

**Como você quer executar o bot?**

### Opção A: Servidor Local/VPS
- [ ] **Sistema Operacional**: `_____________________________`
- [ ] **Recursos (CPU/RAM)**: `_____________________________`
- [ ] **Porta de Execução**: `8000` (padrão)

### Opção B: Docker
- [ ] **Usar Docker?**: [ ] Sim [ ] Não
- [ ] **Docker Compose?**: [ ] Sim [ ] Não

### Opção C: Cloud (AWS, Azure, GCP)
- [ ] **Provedor**: `_____________________________`
- [ ] **Tipo de Serviço**: `_____________________________`

---

## 🔌 10. INTEGRAÇÕES EXTERNAS

### Sistema Contábil Atual
- [ ] **Sistema usado**: `_____________________________`
- [ ] **Tem API?**: [ ] Sim [ ] Não
- [ ] **URL da API**: `_____________________________`
- [ ] **Chave de API**: `_____________________________`

### Webhooks
- [ ] **URL para receber webhooks**: `_____________________________`
- [ ] **Secret para validação**: `_____________________________`

---

## 📊 11. MONITORAMENTO

- [ ] **Usar Sentry (error tracking)?**: [ ] Sim [ ] Não
- [ ] **DSN do Sentry**: `_____________________________`
- [ ] **Usar Prometheus (métricas)?**: [ ] Sim [ ] Não
- [ ] **Porta do Prometheus**: `8001` (padrão)

---

## 🔒 12. SEGURANÇA

- [ ] **Chave Secreta (32+ caracteres)**: `_____________________________`
- [ ] **Chave de Criptografia (32 bytes)**: `_____________________________`
- [ ] **Timeout de Sessão (min)**: `120` (padrão)

---

## 📁 13. ARQUIVOS E BACKUP

### Diretórios
- [ ] **Downloads**: `./data/downloads` (padrão)
- [ ] **Procurações**: `./data/procuracoes` (padrão)
- [ ] **Logs**: `./logs` (padrão)
- [ ] **Backup**: `./backups` (padrão)

### Retenção
- [ ] **Arquivos (dias)**: `90` (padrão)
- [ ] **Logs (dias)**: `30` (padrão)
- [ ] **Backup automático?**: [ ] Sim [ ] Não

---

## 🎯 14. FUNCIONALIDADES DESEJADAS

**Marque o que você quer automatizar:**

### Consultas Automáticas
- [ ] **Simples Nacional** (PGDASD)
  - [ ] Consultar declarações
  - [ ] Gerar DAS
  - [ ] Verificar extratos
  
- [ ] **MEI** (PGMEI)
  - [ ] Consultar dívida ativa
  - [ ] Gerar DAS
  - [ ] Emitir CCMEI
  
- [ ] **DCTFWeb**
  - [ ] Consultar declarações
  - [ ] Baixar XMLs
  - [ ] Gerar guias
  
- [ ] **Caixa Postal**
  - [ ] Verificar mensagens
  - [ ] Baixar documentos
  - [ ] Alertas de prazos
  
- [ ] **Parcelamentos**
  - [ ] Monitorar status
  - [ ] Emitir guias
  - [ ] Alertas de vencimento

### Relatórios e Dashboards
- [ ] **Dashboard web**
- [ ] **Relatórios por email**
- [ ] **API para consultas**
- [ ] **Exportação de dados**

---

## 📞 15. SUPORTE E CONTATO

- [ ] **Forma preferida de contato**: `_____________________________`
- [ ] **Horário de trabalho**: `_____________________________`
- [ ] **Urgência da implementação**: `_____________________________`
- [ ] **Orçamento disponível**: `_____________________________`

---

## ✅ PRÓXIMOS PASSOS

Após receber essas informações, vou:

1. **Configurar o ambiente** com suas credenciais
2. **Implementar as funcionalidades** selecionadas
3. **Configurar o banco de dados** e cache
4. **Testar a integração** com Integra Contador
5. **Configurar notificações** e monitoramento
6. **Entregar documentação** completa
7. **Treinar sua equipe** no uso do sistema

---

## 📝 OBSERVAÇÕES IMPORTANTES

1. **Segurança**: Todas as credenciais serão criptografadas
2. **Backup**: Configuração automática de backup
3. **Logs**: Auditoria completa de todas as operações
4. **Suporte**: 30 dias de suporte incluído
5. **Atualizações**: Compatibilidade com mudanças da API

---

**💡 Dica**: Preencha o máximo de informações possível. Itens em branco usarão valores padrão seguros.

**📧 Envie para**: seu@email.com  
**💬 WhatsApp**: (xx) xxxxx-xxxx  
**🕐 Prazo**: 48h após recebimento das informações 