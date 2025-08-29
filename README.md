# 🔧 MikroTik Backup System

> **Sistema automatizado para backup de configurações MikroTik (.rsc) via SSH**
> 
> Solução completa com agendamento inteligente, notificações Telegram e interface Docker.

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)](https://www.python.org/)
[![MikroTik](https://img.shields.io/badge/MikroTik-Compatible-red?logo=mikrotik)](https://mikrotik.com/)

---

## 🚀 Instalação Rápida

### Pré-requisitos
- Docker e Docker Compose instalados
- Acesso SSH aos dispositivos MikroTik
- (Opcional) Bot do Telegram para notificações

### Passos de Instalação

**1. Clone e acesse o projeto**
```bash
git clone <repository-url>
cd backup-mikrotik
```

**2. Configure as variáveis de ambiente**
```bash
cp .env.example .env
nano .env  # Edite conforme suas necessidades
```

**3. Configure seus dispositivos MikroTik**
```bash
mkdir -p config
cp config/devices.example.json config/devices.json
nano config/devices.json  # Adicione seus dispositivos
```

**4. Inicie o sistema**
```bash
docker compose up -d --build
```

**✅ Pronto!** O sistema está rodando com agendamento automático às 02:00 UTC.

## ✨ Funcionalidades Principais

### 🔐 Conectividade e Segurança
- **Conexão SSH segura** - Autenticação por usuário/senha
- **Multi-dispositivo** - Suporte a múltiplos roteadores MikroTik
- **Timeout configurável** - Controle de tempo limite das conexões
- **Backup .rsc exclusivo** - Apenas arquivos de configuração em texto

### 🤖 Automação e Agendamento
- **Scheduler integrado** - Agendamento interno sem dependência do cron
- **Configuração flexível** - Horários personalizáveis via CRON_SCHEDULE
- **Execução automática** - Inicialização automática do container
- **Recuperação de falhas** - Logs detalhados para diagnóstico

### 📱 Notificações e Monitoramento
- **Notificações Telegram** - Relatórios automáticos de backup
- **Logs estruturados** - Sistema de logging com níveis configuráveis
- **Estatísticas detalhadas** - Informações sobre arquivos e tamanhos
- **Limpeza automática** - Remoção de backups antigos configurável

---

## ⚙️ Configuração Detalhada

### Variáveis de Ambiente (.env)

```bash
# Agendamento do backup
CRON_SCHEDULE="0 2 * * *"          # Diário às 02:00 UTC

# Fuso horário
TZ=UTC                             # Ex: America/Sao_Paulo, Europe/London

# Notificações Telegram (opcional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# Configurações de backup
BACKUP_RETENTION_DAYS=30           # Manter backups por 30 dias

# Configurações SSH
SSH_TIMEOUT=30                     # Timeout em segundos

# Logs
LOG_LEVEL=INFO                     # DEBUG, INFO, WARNING, ERROR
```

### Configuração de Dispositivos (config/devices.json)

```json
{
  "devices": [
    {
      "name": "mikrotik-matriz",
      "host": "192.168.1.1",
      "username": "admin",
      "password": "sua_senha_segura",
      "port": 22
    },
    {
      "name": "mikrotik-filial",
      "host": "10.0.0.1",
      "username": "backup-user",
      "password": "outra_senha_segura",
      "port": 2222
    }
  ]
}
```

**1. Criar um Bot no Telegram:**
- Converse com [@BotFather](https://t.me/botfather)
- Use `/newbot` e siga as instruções
- Copie o token gerado

**2. Obter o Chat ID:**
- Para chat privado: converse com [@userinfobot](https://t.me/userinfobot)
- Para grupos: adicione o bot ao grupo e use `/start`

**3. Testar as notificações:**
```bash
# Teste rápido das notificações
./scripts/test-telegram-group.sh
```

---

## 🎯 Comandos Úteis

### Gerenciamento do Sistema

```bash
# Iniciar o sistema
docker compose up -d --build

# Parar o sistema
docker compose down

# Reiniciar o sistema
docker compose restart mikrotik-backup

# Verificar status
docker compose ps

# Ver logs em tempo real
docker compose logs -f mikrotik-backup
```

### Execução de Backups

```bash
# Executar backup manual de todos os dispositivos
docker compose exec mikrotik-backup python src/mikrotik_backup.py run-once

# Executar backup usando script auxiliar
./scripts/backup-manual.sh

# Ver estatísticas dos backups
docker compose exec mikrotik-backup python src/mikrotik_backup.py stats

# Limpar backups antigos manualmente
docker compose exec mikrotik-backup python src/mikrotik_backup.py cleanup
```

### Monitoramento e Logs

```bash
# Ver logs do dia atual
docker compose exec mikrotik-backup cat /app/logs/mikrotik_backup_$(date +%Y%m%d).log

# Listar todos os backups
docker compose exec mikrotik-backup find /app/backups -name "*.rsc" -ls

# Verificar espaço em disco
docker compose exec mikrotik-backup df -h /app/backups/

# Copiar backup específico para o host
docker compose cp mikrotik-backup:/app/backups/dispositivo/arquivo.rsc ./
```

### Testes e Notificações

```bash
# Testar notificação Telegram
docker compose exec mikrotik-backup python src/mikrotik_backup.py test-telegram

# Testar notificações em grupos
./scripts/test-telegram-group.sh

# Testar performance do backup
./scripts/test-performance.sh
```

---

## ⏰ Agendamento Automático

O sistema utiliza um **scheduler Python integrado** configurado via variável `CRON_SCHEDULE`:

| Agendamento | Configuração | Descrição |
|-------------|--------------|----------|
| Diário às 02:00 | `"0 2 * * *"` | Padrão do sistema |
| A cada 6 horas | `"0 */6 * * *"` | Para ambientes críticos |
| Segunda a sexta às 08:00 | `"0 8 * * 1-5"` | Horário comercial |
| Semanal (domingo às 03:00) | `"0 3 * * 0"` | Para redes pequenas |

## 📁 Estrutura de Arquivos

### Diretórios do Projeto
```
backup-mikrotik/
├── 📁 config/
│   ├── devices.json              # Configuração dos dispositivos
│   └── devices.example.json      # Exemplo de configuração
├── 📁 src/
│   └── mikrotik_backup.py        # Script principal
├── 📁 scripts/
│   ├── backup-manual.sh          # Backup manual
│   ├── cleanup.sh                # Limpeza de arquivos antigos
│   ├── start.sh                  # Inicialização do sistema
│   ├── test-performance.sh       # Teste de performance
│   └── test-telegram-group.sh    # Teste de notificações
├── 📁 backups/                   # Arquivos de backup (.rsc)
├── 📁 logs/                      # Logs da aplicação
├── 📄 docker-compose.yml         # Configuração Docker
├── 📄 Dockerfile                 # Imagem Docker
├── 📄 requirements.txt           # Dependências Python
├── 📄 .env.example               # Exemplo de variáveis
└── 📄 README.md                  # Esta documentação
```

### Estrutura dos Backups
```
backups/
├── mikrotik-matriz/
│   ├── mikrotik-matriz_20250127_020001.rsc
│   ├── mikrotik-matriz_20250126_020001.rsc
│   └── ...
└── mikrotik-filial/
    ├── mikrotik-filial_20250127_020001.rsc
    ├── mikrotik-filial_20250126_020001.rsc
    └── ...
```

### Convenção de Nomenclatura
- **Backups**: `{nome_dispositivo}_{YYYYMMDD}_{HHMMSS}.rsc`
- **Logs**: `mikrotik_backup_{YYYYMMDD}.log`

---

## 🛠️ Solução de Problemas

### Problemas Comuns

#### 🔴 Container não inicia

```bash
# Verificar logs de inicialização
docker compose logs mikrotik-backup

# Verificar arquivo .env
cat .env | grep -v "^#" | grep -v "^$"

# Reconstruir imagem
docker compose down && docker compose up -d --build
```

#### 🔴 Erro de conexão SSH

```bash
# Testar conectividade de rede
docker compose exec mikrotik-backup ping -c 3 192.168.1.1

# Testar porta SSH
docker compose exec mikrotik-backup nc -zv 192.168.1.1 22

# Verificar configuração do dispositivo
cat config/devices.json | jq '.devices[0]'
```

#### 🔴 Notificações Telegram não funcionam

```bash
# Testar notificação
docker compose exec mikrotik-backup python src/mikrotik_backup.py test-telegram

# Verificar configurações
docker compose exec mikrotik-backup env | grep TELEGRAM
```

### Debug Avançado

```bash
# Habilitar logs de debug
echo "LOG_LEVEL=DEBUG" >> .env
docker compose restart mikrotik-backup

# Executar backup com debug
docker compose exec mikrotik-backup python src/mikrotik_backup.py run-once
```

---

## 🔒 Segurança e Melhores Práticas

### Recomendações de Segurança
- **Usuários dedicados**: Crie usuários específicos para backup (não use admin)
- **Senhas fortes**: Use senhas complexas e únicas
- **Acesso restrito**: Limite o acesso SSH por IP quando possível
- **Atualizações**: Mantenha Docker e dependências atualizados
- **Monitoramento**: Revise os logs regularmente

### Configuração Segura no MikroTik
```bash
# Criar usuário específico para backup
/user add name=backup-user password=senha_forte group=read

# Verificar permissões
/user print
```

### Backup dos Dados
- Os backups são armazenados em volumes Docker persistentes
- Considere fazer backup dos volumes para armazenamento externo
- Configure retenção adequada baseada na sua política de backup

---

### Recursos Úteis
- **Logs**: Sempre verifique os logs em caso de problemas
- **Scripts auxiliares**: Use os scripts em `./scripts/` para tarefas comuns
- **Documentação MikroTik**: [RouterOS Documentation](https://help.mikrotik.com/)

---

<div align="center">

**🔧 MikroTik Backup System**

*Sistema automatizado para backup seguro de configurações MikroTik*

**Desenvolvido com ❤️ para a comunidade de redes**

</div>



</div>