#!/bin/bash

# Script para testar notificações do Telegram em grupos
echo "📱 Testando notificações do Telegram para grupos..."
echo "⚠️  Certifique-se de que:"
echo "   1. O bot foi adicionado ao grupo"
echo "   2. O bot tem permissões para enviar mensagens"
echo "   3. O TELEGRAM_CHAT_ID no .env é o ID do grupo (número negativo)"
echo ""
echo "🔧 Executando teste..."

# Executar teste do Telegram
docker compose exec mikrotik-backup python src/mikrotik_backup.py test-telegram

echo ""
echo "✅ Se a mensagem foi enviada com sucesso, verifique o grupo do Telegram!"
echo "❌ Se houve erro 400, verifique se o bot tem as permissões corretas no grupo."
echo "❌ Se houve erro 404, verifique se o TELEGRAM_CHAT_ID está correto."