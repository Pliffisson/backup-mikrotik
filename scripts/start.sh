#!/bin/bash

# Script para iniciar o sistema de backup MikroTik

echo "🚀 Iniciando sistema de backup MikroTik..."

# Verificar se o arquivo .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Arquivo .env não encontrado!"
    echo "📋 Copiando .env.example para .env..."
    cp .env.example .env
    echo "✏️  Por favor, edite o arquivo .env com suas configurações antes de continuar."
    echo "📝 Configure especialmente:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - TELEGRAM_CHAT_ID"
    exit 1
fi

# Verificar se o arquivo de dispositivos existe
if [ ! -f "config/devices.json" ]; then
    echo "⚠️  Arquivo config/devices.json não encontrado!"
    echo "📝 Por favor, configure seus dispositivos MikroTik no arquivo config/devices.json"
    exit 1
fi

# Criar diretórios necessários
mkdir -p backups logs

# Construir e iniciar containers
echo "🔨 Construindo containers..."
docker compose build

echo "▶️  Iniciando serviços..."
docker compose up -d

# Verificar status
echo "📊 Status dos serviços:"
docker compose ps

echo "✅ Sistema iniciado com sucesso!"
echo "📋 Para verificar logs: docker compose logs -f mikrotik-backup"
echo "🛑 Para parar: docker compose down"
echo "🔄 Para reiniciar: docker compose restart"