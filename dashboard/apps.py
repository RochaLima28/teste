from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard'
    
    def ready(self):
        """Inicializar quando a aplicação estiver pronta"""
        # Importar aqui para evitar problemas de importação circular
        import os
        if os.environ.get('RUN_MAIN') or os.environ.get('WERKZEUG_RUN_MAIN'):
            # Só executar no processo principal (não no reloader)
            self.start_file_monitor()
    
    def start_file_monitor(self):
        """Iniciar o monitoramento de arquivos"""
        try:
            from django.conf import settings
            from .utils.file_monitor import FileMonitor
            from .utils.excel_processor import ExcelProcessor
            from . import views
            from channels.layers import get_channel_layer
            from asgiref.sync import async_to_sync
            from datetime import datetime
            
            processor = ExcelProcessor()
            monitor = FileMonitor(
                settings.WATCH_FOLDER,
                settings.EXCEL_PATTERN,
                settings.CHECK_INTERVAL
            )
            
            def on_file_changed(file_path: str):
                """Callback quando arquivo é detectado/modificado"""
                try:
                    logger.info(f"Processando arquivo: {file_path}")
                    
                    # Processar arquivo
                    companies = processor.process_file(file_path)
                    
                    # Aplicar ajustes do banco de dados
                    companies = views.apply_adjustments_to_companies(companies)
                    
                    statistics = processor.get_statistics(companies)
                    
                    # Atualizar dados
                    views.current_data['companies'] = companies
                    views.current_data['statistics'] = statistics
                    views.current_data['file_path'] = file_path
                    views.current_data['last_update'] = datetime.now().isoformat()
                    
                    # Emitir atualização para todos os clientes conectados via Channels
                    channel_layer = get_channel_layer()
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            "dashboard",
                            {
                                "type": "dashboard.update",
                                "data": views.current_data
                            }
                        )
                    
                    logger.info(f"Dados atualizados: {len(companies)} empresas")
                
                except Exception as e:
                    logger.error(f"Erro ao processar arquivo: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Iniciar monitor
            if monitor.start(on_file_changed):
                logger.info("Monitor de arquivo iniciado")
            else:
                logger.warning("Falha ao iniciar monitor de arquivo")
        
        except Exception as e:
            logger.error(f"Erro ao inicializar monitor: {e}")
            import traceback
            traceback.print_exc()
