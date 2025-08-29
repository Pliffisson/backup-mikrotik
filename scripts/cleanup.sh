#!/bin/bash

# Script para limpeza de backups antigos

# Configurações
DAYS_TO_KEEP=${1:-30}  # Padrão: manter 30 dias
BACKUP_DIR="./backups"
LOG_DIR="./logs"

echo "🧹 Iniciando limpeza de arquivos antigos..."
echo "📅 Mantendo arquivos dos últimos $DAYS_TO_KEEP dias"

# Função para limpeza
cleanup_directory() {
    local dir=$1
    local description=$2
    
    if [ -d "$dir" ]; then
        echo "🔍 Verificando $description em: $dir"
        
        # Encontrar e remover arquivos antigos
        files_removed=$(find "$dir" -type f -mtime +$DAYS_TO_KEEP -print -delete | wc -l)
        
        if [ $files_removed -gt 0 ]; then
            echo "🗑️  Removidos $files_removed arquivo(s) de $description"
        else
            echo "✅ Nenhum arquivo antigo encontrado em $description"
        fi
    else
        echo "⚠️  Diretório $dir não encontrado"
    fi
}

# Limpar backups antigos
cleanup_directory "$BACKUP_DIR" "backups"

# Limpar logs antigos
cleanup_directory "$LOG_DIR" "logs"

# Limpar containers e imagens não utilizadas
echo "🐳 Limpando recursos Docker não utilizados..."
docker system prune -f

# Estatísticas de espaço
echo "📊 Uso de espaço em disco:"
echo "📁 Backups: $(du -sh $BACKUP_DIR 2>/dev/null | cut -f1 || echo '0B')"
echo "📋 Logs: $(du -sh $LOG_DIR 2>/dev/null | cut -f1 || echo '0B')"

echo "✅ Limpeza concluída!"