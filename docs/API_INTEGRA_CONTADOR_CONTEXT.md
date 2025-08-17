# API INTEGRA CONTADOR - DOCUMENTAÇÃO DE CONTEXTO

## VISÃO GERAL

O **Integra Contador** é uma plataforma de APIs desenvolvida pela Receita Federal em colaboração com o SERPRO, lançada em 26/09/2022. Substitui o acesso robotizado direto ao e-CAC, oferecendo uma interface oficial e estruturada para automação de serviços contábeis e fiscais.

## CARACTERÍSTICAS TÉCNICAS

### Tecnologia Base
- **Protocolo**: REST API
- **Autenticação**: OAuth2 + Certificado Digital e-CNPJ
- **Formato**: JSON
- **Base URL**: `https://gateway.apiserpro.serpro.gov.br/integra-contador/v1`
- **Token URL**: `https://gateway.apiserpro.serpro.gov.br/token`

### Modelo de Autenticação
```
1. Obter Consumer Key + Consumer Secret (Portal SERPRO)
2. Gerar Token Bearer OAuth2 (validade: 1 hora)
3. Usar certificado digital e-CNPJ para procurações
4. Header Authorization: Bearer {token}
```

## FUNCIONALIDADES DISPONÍVEIS (84 TOTAL)

### 📊 CONSULTAS (45 funcionalidades)

#### **SIMPLES NACIONAL (PGDASD)**
- `GET /pgdasd/declaracoes/{cnpj}` - Consultar todas as declarações
- `GET /pgdasd/ultima-declaracao/{cnpj}` - Última declaração/recibo  
- `GET /pgdasd/declaracao/{cnpj}/{periodo}` - Declaração específica
- `GET /pgdasd/extrato-das/{cnpj}/{periodo}` - Extrato do DAS

#### **MEI (PGMEI)**
- `GET /pgmei/divida-ativa/{cnpj}` - Consultar dívida ativa
- `GET /pgmei/situacao/{cnpj}` - Situação do MEI

#### **CCMEI (Certificado MEI)**
- `GET /ccmei/dados/{cnpj}` - Consultar dados CCMEI
- `GET /ccmei/situacao-cadastral/{cnpj}` - Situação cadastral

#### **DCTFWEB**
- `GET /dctfweb/recibo/{cnpj}/{periodo}` - Recibo da declaração
- `GET /dctfweb/declaracao-completa/{cnpj}/{periodo}` - Declaração completa
- `GET /dctfweb/xml/{cnpj}/{periodo}` - XML da declaração
- `GET /dctfweb/apuracao-mit/{cnpj}/{periodo}` - Apuração MIT
- `GET /dctfweb/apuracoes-mit/{cnpj}/{ano}` - Todas apurações MIT (ano)
- `GET /dctfweb/apuracoes-mit/{cnpj}/{ano}/{mes}` - Apurações MIT (mês)

#### **PROCURAÇÕES**
- `GET /procuracoes/{cnpj}` - Obter procurações do contribuinte

#### **CAIXA POSTAL (e-CAC)**
- `GET /caixa-postal/mensagens/{cnpj}` - Lista de mensagens
- `GET /caixa-postal/mensagem/{cnpj}/{id}` - Detalhes de mensagem específica
- `GET /caixa-postal/indicador-novas/{cnpj}` - Indicador de novas mensagens

#### **PARCELAMENTOS**
Suporte para todos os tipos: PARCSN, PERTSN, RELPSN, PARCMEI, PERTMEI, RELPMEI, PARCSN ESPECIAL, PARCMEI ESPECIAL

Para cada tipo:
- `GET /{tipo}/pedidos/{cnpj}` - Consultar pedidos de parcelamento
- `GET /{tipo}/parcelamento/{cnpj}/{numero}` - Consultar parcelamento específico
- `GET /{tipo}/detalhes-pagamento/{cnpj}/{numero}/{parcela}` - Detalhes de pagamento
- `GET /{tipo}/parcelas-impressao/{cnpj}/{numero}` - Parcelas disponíveis para impressão

#### **PAGAMENTOS**
- `GET /pagamento/documento-arrecadacao/{cnpj}/{numero}` - Consultar documento pago

#### **DTE (Documento de Transferência Eletrônica)**
- `GET /dte/indicador/{cnpj}` - Obter indicador DTE

### 📄 EMISSÕES (20 funcionalidades)

#### **SIMPLES NACIONAL**
- `POST /pgdasd/gerar-das/{cnpj}/{periodo}` - Gerar DAS

#### **MEI**
- `POST /pgmei/gerar-das-pdf/{cnpj}/{periodo}` - Gerar DAS em PDF
- `POST /pgmei/gerar-das-codigobarras/{cnpj}/{periodo}` - Gerar DAS código de barras
- `PUT /pgmei/atualizar-beneficio/{cnpj}` - Atualizar benefício

#### **CCMEI**
- `POST /ccmei/emitir/{cnpj}` - Emitir CCMEI

#### **DCTFWEB**
- `POST /dctfweb/gerar-guia/{cnpj}/{periodo}` - Gerar guia de declaração
- `POST /dctfweb/gerar-documento-arrecadacao/{cnpj}/{periodo}` - Doc. arrecadação

#### **SICALC/DARF**
- `POST /sicalc/consolidar-emitir-darf/{cnpj}/{periodo}` - Consolidar e emitir DARF

#### **COMPROVANTES E RELATÓRIOS**
- `POST /pagamento/gerar-comprovante/{cnpj}/{numero}` - Comprovante de pagamento
- `POST /sitfis/solicitar-relatorio/{cnpj}` - Solicitar relatório situação fiscal
- `GET /sitfis/emitir-relatorio/{cnpj}/{protocolo}` - Emitir relatório situação fiscal

#### **PARCELAMENTOS - EMISSÃO**
Para todos os tipos de parcelamento:
- `POST /{tipo}/emitir-documento/{cnpj}/{numero}/{parcela}` - Emitir documento de arrecadação

### 📋 TRANSMISSÕES/ENTREGAS (3 funcionalidades)

#### **DECLARAÇÕES**
- `POST /pgdasd/entregar-declaracao/{cnpj}` - Entregar declaração Simples Nacional
- `POST /dctfweb/transmitir-declaracao/{cnpj}` - Transmitir declaração DCTFWeb
- `POST /defis/transmitir-declaracao/{cnpj}` - Transmitir DEFIS

## ESTRUTURAS DE DADOS

### Autenticação OAuth2
```json
{
  "grant_type": "client_credentials",
  "consumer_key": "string",
  "consumer_secret": "string"
}
```

### Resposta Token
```json
{
  "access_token": "string",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "default"
}
```

### Headers Padrão
```http
Authorization: Bearer {access_token}
Content-Type: application/json
X-Request-ID: {uuid} (opcional)
```

### Estrutura Resposta Padrão
```json
{
  "success": true,
  "data": {},
  "message": "string",
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}
```

### Estrutura de Erro
```json
{
  "success": false,
  "error": {
    "code": "string",
    "message": "string",
    "details": ["string"]
  },
  "timestamp": "2024-01-01T00:00:00Z",
  "request_id": "uuid"
}
```

## CÓDIGOS DE RESPOSTA HTTP

| Código | Descrição | Ação |
|--------|-----------|------|
| 200 | Sucesso | Requisição processada com sucesso |
| 201 | Criado | Recurso criado com sucesso |
| 400 | Bad Request | Verificar parâmetros da requisição |
| 401 | Unauthorized | Token inválido ou expirado - renovar |
| 403 | Forbidden | Sem permissão - verificar procurações |
| 404 | Not Found | Recurso não encontrado |
| 429 | Rate Limit | Aguardar antes de nova requisição |
| 500 | Server Error | Erro interno - tentar novamente |
| 503 | Service Unavailable | Serviço temporariamente indisponível |

## PROCURAÇÕES E PERMISSÕES

### Tipos de Acesso
1. **Direto**: Proprietário do CNPJ/CPF
2. **Procuração**: Via sistema de procurações eletrônicas e-CAC
3. **Software House**: XML assinado digitalmente pelo procurador

### Validação de Procuração
```json
{
  "cnpj_contribuinte": "string",
  "cpf_procurador": "string", 
  "servicos_autorizados": ["string"],
  "data_inicio": "date",
  "data_fim": "date",
  "ativa": true
}
```

## RATE LIMITING E THROTTLING

### Limites Conhecidos
- Token OAuth2: 1 hora de validade
- Requisições por minuto: Não documentado oficialmente
- Timeout de requisição: 30 segundos recomendado

### Boas Práticas
1. Cache de tokens até expirar
2. Retry com backoff exponencial
3. Processar em lotes quando possível
4. Monitorar headers de rate limit

## AMBIENTES

### Produção
- **Base URL**: `https://gateway.apiserpro.serpro.gov.br/integra-contador/v1`
- **Token URL**: `https://gateway.apiserpro.serpro.gov.br/token`

### Homologação
- **Base URL**: `https://gateway.apiserpro.serpro.gov.br/integra-contador-hom/v1`
- **Token URL**: `https://gateway.apiserpro.serpro.gov.br/token`

## MONITORAMENTO E LOGS

### Headers de Debug
```http
X-Request-ID: {uuid}
X-Correlation-ID: {uuid}
User-Agent: BotECAC/1.0
```

### Métricas Importantes
- Taxa de sucesso por endpoint
- Tempo de resposta médio
- Frequência de renovação de token
- Uso por tipo de consulta

## CERTIFICAÇÃO DIGITAL

### Requisitos
- Certificado e-CNPJ válido (ICP-Brasil)
- Formato: A1 ou A3
- Usado para: Visualizar credenciais no portal + Procurações

### Fluxo com Certificado
1. Autenticação OAuth2 (Consumer Key/Secret)
2. Apresentação do certificado e-CNPJ (para serviços com procuração)
3. Validação da procuração eletrônica
4. Acesso autorizado aos dados

## CASOS DE USO COMUNS

### 1. Consulta Mensal Simples Nacional
```
1. Obter token OAuth2
2. Consultar últimas declarações PGDASD
3. Verificar pendências no caixa postal
4. Gerar DAS se necessário
```

### 2. Monitoramento de Parcelamentos
```
1. Consultar todos os parcelamentos ativos
2. Verificar parcelas vencendo
3. Emitir guias de pagamento
4. Atualizar status interno
```

### 3. Gestão de Caixa Postal
```
1. Verificar indicador de novas mensagens
2. Listar mensagens não lidas
3. Baixar detalhes de cada mensagem
4. Processar intimações e prazos
```

## INTEGRAÇÃO COM SISTEMAS

### Banco de Dados Local
- Cache de tokens e credenciais
- Histórico de consultas e respostas
- Controle de procurações por cliente
- Log de operações para auditoria

### Notificações
- Webhooks para eventos importantes
- Email/SMS para prazos críticos
- Dashboard em tempo real
- Relatórios automatizados

---

**Versão**: 1.0  
**Última Atualização**: Janeiro 2025  
**Fonte**: Documentação oficial SERPRO + Pesquisa técnica 