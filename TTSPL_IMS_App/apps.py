from django.apps import AppConfig
import threading


class TtsplImsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'TTSPL_IMS_App'
    
    def ready(self):
        # Optional: Import signals when the app is ready
        import TTSPL_IMS_App.signals

        from TTSPL_IMS_App.scheduler import start_scheduler
        scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
        scheduler_thread.start()
