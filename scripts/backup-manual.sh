#!/bin/bash

# Script para executar backup manual dos dispositivos MikroTik

echo "🔧 Executando backup manual..."

# Verificar se o container está rodando
if ! docker compose ps | grep -q "mikrotik-backup.*Up"; then
    echo "⚠️  Container mikrotik-backup não está rodando!"
    echo "🚀 Iniciando container..."
    docker compose up -d mikrotik-backup
    sleep 10
fi

# Executar backup
echo "📦 Iniciando processo de backup..."
docker compose exec mikrotik-backup python src/mikrotik_backup.py run-once

echo "✅ Backup manual concluído!"
echo "📁 Verifique os arquivos em: ./backups/"
echo "📋 Logs disponíveis em: ./logs/"