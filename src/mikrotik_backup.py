#!/usr/bin/env python3
"""
MikroTik Backup Script - RSC Only
Script para realizar backup de configuração (.rsc) de dispositivos MikroTik via SSH
"""

import os
import sys
import json
import time
import logging
import paramiko
import requests
import schedule
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class MikroTikBackup:
    def __init__(self, config_file='config/devices.json'):
        self.config_file = config_file
        self.backup_dir = Path('backups')
        self.logs_dir = Path('logs')
        self.setup_logging()
        self.devices = self.load_devices_config()
        
        # Configurações do Telegram
        self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # Configurações de performance
        self.ssh_timeout = int(os.getenv('SSH_TIMEOUT', '30'))
        
    def setup_logging(self):
        """Configurar sistema de logging"""
        self.logs_dir.mkdir(exist_ok=True)
        
        # Configurar formato do log
        log_format = '%(asctime)s - %(levelname)s - %(message)s'
        log_level = getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
        
        # Configurar logging para arquivo
        log_file = self.logs_dir / f'mikrotik_backup_{datetime.now().strftime("%Y%m%d")}.log'
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def load_devices_config(self):
        """Carregar configuração dos dispositivos"""
        try:
            with open(self.config_file, 'r') as f:
                config = json.load(f)
                return config.get('devices', [])
        except FileNotFoundError:
            self.logger.error(f"Arquivo de configuração {self.config_file} não encontrado")
            return []
        except json.JSONDecodeError:
            self.logger.error(f"Erro ao decodificar JSON do arquivo {self.config_file}")
            return []
            
    def connect_ssh(self, device):
        """Estabelecer conexão SSH com o dispositivo"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.logger.info(f"Conectando ao dispositivo {device['name']} ({device['host']})")
            
            ssh.connect(
                hostname=device['host'],
                port=device.get('port', 22),
                username=device['username'],
                password=device['password'],
                timeout=self.ssh_timeout
            )
            
            return ssh
            
        except Exception as e:
            self.logger.error(f"Erro ao conectar com {device['name']}: {str(e)}")
            return None
            
    def execute_command(self, ssh, command, timeout=30):
        """Executar comando via SSH"""
        try:
            stdin, stdout, stderr = ssh.exec_command(command, timeout=timeout)
            output = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')
            
            if error:
                self.logger.warning(f"Aviso no comando '{command}': {error}")
                
            return output
            
        except Exception as e:
            self.logger.error(f"Erro ao executar comando '{command}': {str(e)}")
            return None
            
    def create_backup(self, device):
        """Criar backup .rsc do dispositivo MikroTik"""
        ssh = self.connect_ssh(device)
        if not ssh:
            return False
            
        try:
            device_name = device['name']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # Criar diretório para o dispositivo
            device_backup_dir = self.backup_dir / device_name
            device_backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Nome do arquivo de backup .rsc
            export_filename = f"{device_name}_{timestamp}.rsc"
            
            self.logger.info(f"Iniciando backup .rsc do dispositivo {device_name}")
            
            # Exportar configuração em formato .rsc
            export_command = f"/export file={export_filename}"
            self.execute_command(ssh, export_command)
            
            # Aguardar criação do arquivo
            time.sleep(3)
            
            # Baixar arquivo via SFTP
            sftp = ssh.open_sftp()
            
            try:
                remote_export = f"/{export_filename}"
                local_export = device_backup_dir / export_filename
                sftp.get(remote_export, str(local_export))
                self.logger.info(f"Backup .rsc baixado: {local_export}")
                
                # Remover arquivo remoto
                sftp.remove(remote_export)
                
                # Verificar se o arquivo foi criado e tem conteúdo
                if local_export.exists() and local_export.stat().st_size > 0:
                    self.logger.info(f"Backup do dispositivo {device_name} concluído com sucesso")
                    success = True
                else:
                    self.logger.error(f"Arquivo de backup vazio ou não criado: {local_export}")
                    success = False
                    
            except Exception as e:
                self.logger.error(f"Erro ao baixar backup .rsc: {str(e)}")
                success = False
                
            sftp.close()
            ssh.close()
            
            return success
            
        except Exception as e:
            self.logger.error(f"Erro durante backup do dispositivo {device['name']}: {str(e)}")
            if ssh:
                ssh.close()
            return False
            
    def cleanup_old_backups(self, days_to_keep=None):
        """Limpar backups antigos"""
        if days_to_keep is None:
            days_to_keep = int(os.getenv('BACKUP_RETENTION_DAYS', '30'))
            
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        removed_count = 0
        
        for device_dir in self.backup_dir.iterdir():
            if device_dir.is_dir():
                for backup_file in device_dir.iterdir():
                    if backup_file.is_file() and backup_file.suffix == '.rsc':
                        file_time = datetime.fromtimestamp(backup_file.stat().st_mtime)
                        if file_time < cutoff_date:
                            backup_file.unlink()
                            self.logger.info(f"Backup antigo removido: {backup_file}")
                            removed_count += 1
                            
        if removed_count > 0:
            self.logger.info(f"Total de {removed_count} backups antigos removidos")
        else:
            self.logger.info("Nenhum backup antigo para remover")
                            
    def send_telegram_notification(self, message):
        """Enviar notificação via Telegram (suporte a usuários e grupos)"""
        if not self.telegram_token or not self.telegram_chat_id:
            self.logger.warning("Configurações do Telegram não encontradas")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            
            # Formatação melhorada da mensagem
            formatted_message = f"🔧 <b>MikroTik Backup System (.rsc)</b>\n\n{message}"
            
            data = {
                'chat_id': self.telegram_chat_id,
                'text': formatted_message,
                'parse_mode': 'HTML',
                'disable_web_page_preview': True,
                'disable_notification': False
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                chat_type = "grupo" if str(self.telegram_chat_id).startswith('-') else "usuário"
                self.logger.info(f"Notificação Telegram enviada com sucesso para {chat_type}")
                return True
            else:
                self.logger.error(f"Erro ao enviar Telegram: {response.status_code}")
                if response.status_code == 400:
                    self.logger.error("Verifique se o bot foi adicionado ao grupo e tem permissões para enviar mensagens")
                return False
                
        except Exception as e:
            self.logger.error(f"Erro ao enviar notificação Telegram: {str(e)}")
            return False
            
    def get_backup_stats(self):
        """Obter estatísticas dos backups"""
        stats = {}
        total_files = 0
        total_size = 0
        
        for device_dir in self.backup_dir.iterdir():
            if device_dir.is_dir():
                device_files = list(device_dir.glob('*.rsc'))
                device_count = len(device_files)
                device_size = sum(f.stat().st_size for f in device_files)
                
                stats[device_dir.name] = {
                    'files': device_count,
                    'size_mb': round(device_size / (1024 * 1024), 2)
                }
                
                total_files += device_count
                total_size += device_size
                
        stats['total'] = {
            'files': total_files,
            'size_mb': round(total_size / (1024 * 1024), 2)
        }
        
        return stats
            
    def run_backup(self):
        """Executar backup de todos os dispositivos"""
        if not self.devices:
            self.logger.error("Nenhum dispositivo configurado")
            return
            
        self.logger.info("Iniciando processo de backup .rsc")
        start_time = datetime.now()
        
        success_count = 0
        failed_devices = []
        successful_devices = []
        
        # Criar diretório de backups
        self.backup_dir.mkdir(exist_ok=True)
        
        for device in self.devices:
            if self.create_backup(device):
                success_count += 1
                successful_devices.append(device['name'])
            else:
                failed_devices.append(device['name'])
                
        end_time = datetime.now()
        duration = end_time - start_time
        
        # Limpar backups antigos
        self.cleanup_old_backups()
        
        # Obter estatísticas
        stats = self.get_backup_stats()
        
        # Preparar mensagem de resultado
        total_devices = len(self.devices)
        failed_count = len(failed_devices)
        
        message = f"📊 <b>Relatório de Backup MikroTik (.rsc)</b>\n\n"
        message += f"🕐 <b>Horário:</b> {start_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
        message += f"⏱️ <b>Duração:</b> {duration}\n\n"
        message += f"✅ <b>Sucessos:</b> {success_count}/{total_devices}\n"
        
        if successful_devices:
            message += f"\n<b>✅ Dispositivos com Sucesso:</b>\n"
            for device in successful_devices:
                if device in stats:
                    files = stats[device]['files']
                    size = stats[device]['size_mb']
                    message += f"• {device} ({files} arquivos, {size}MB)\n"
                else:
                    message += f"• {device}\n"
        
        if failed_devices:
            message += f"\n❌ <b>Falhas:</b> {failed_count}\n"
            message += f"<b>Dispositivos com falha:</b>\n"
            for device in failed_devices:
                message += f"• {device}\n"
        else:
            message += f"\n🎉 <b>Todos os backups foram realizados com sucesso!</b>"
            
        # Adicionar estatísticas totais
        if stats['total']['files'] > 0:
            message += f"\n📈 <b>Total:</b> {stats['total']['files']} arquivos .rsc ({stats['total']['size_mb']}MB)"
            
        self.logger.info(f"Backup concluído: {success_count}/{total_devices} sucessos")
        
        # Enviar notificação
        self.send_telegram_notification(message)
        
    def schedule_backups(self):
        """Agendar backups automáticos"""
        cron_schedule = os.getenv('CRON_SCHEDULE', '0 2 * * *')
        
        # Converter cron para schedule (simplificado)
        if cron_schedule == '0 2 * * *':  # Diário às 02:00
            schedule.every().day.at("02:00").do(self.run_backup)
            self.logger.info("Agendamento configurado: Backup diário às 02:00")
        elif cron_schedule == '0 */6 * * *':  # A cada 6 horas
            schedule.every(6).hours.do(self.run_backup)
            self.logger.info("Agendamento configurado: Backup a cada 6 horas")
        else:
            # Padrão: diário às 02:00
            schedule.every().day.at("02:00").do(self.run_backup)
            self.logger.info(f"Usando agendamento padrão (diário às 02:00) - CRON_SCHEDULE: {cron_schedule}")
        
        self.logger.info("Iniciando agendador de backups...")
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verificar a cada minuto
            
def main():
    """Função principal"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        backup_manager = MikroTikBackup()
        
        if command == "run-once":
            backup_manager.run_backup()
        elif command == "schedule":
            backup_manager.schedule_backups()
        elif command == "test-telegram":
            backup_manager.send_telegram_notification("🧪 Teste de notificação MikroTik Backup (.rsc)")
        elif command == "cleanup":
            backup_manager.cleanup_old_backups()
        elif command == "stats":
            stats = backup_manager.get_backup_stats()
            print(json.dumps(stats, indent=2))
        else:
            print("Uso: python mikrotik_backup.py [run-once|schedule|test-telegram|cleanup|stats]")
    else:
        print("Uso: python mikrotik_backup.py [run-once|schedule|test-telegram|cleanup|stats]")
        
if __name__ == "__main__":
    main()