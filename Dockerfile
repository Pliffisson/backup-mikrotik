FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    openssh-client \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copiar arquivos de requisitos
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fonte
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Criar diretórios necessários
RUN mkdir -p backups logs

# Tornar scripts executáveis
RUN chmod +x scripts/*.sh

# Criar usuário não-root
RUN if ! id -u mikrotik-backup >/dev/null 2>&1; then \
        adduser --disabled-password --gecos '' --uid 1000 mikrotik-backup; \
    fi && \
    chown -R mikrotik-backup:mikrotik-backup /app
USER mikrotik-backup

# Comando padrão
CMD ["python", "src/mikrotik_backup.py", "schedule"]