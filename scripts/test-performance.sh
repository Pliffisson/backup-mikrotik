#!/bin/bash

# Script para testar performance do backup
echo "🚀 Testando performance do backup otimizado..."
echo "⏰ Iniciando em: $(date)"

start_time=$(date +%s)

# Executar backup com medição de tempo
docker compose exec mikrotik-backup python src/mikrotik_backup.py run-once

end_time=$(date +%s)
duration=$((end_time - start_time))

echo "⏱️  Backup concluído em: ${duration} segundos"
echo "📁 Verificando arquivos gerados:"
ls -la backups/*/

echo "📋 Últimas linhas do log:"
tail -10 logs/backup_$(date +%Y%m%d).log