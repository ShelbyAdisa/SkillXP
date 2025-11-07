from django.apps import AppConfig

class ElibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'elibrary'
    verbose_name = 'eLibrary Management'
    
    def ready(self):
        """
        Import signals when the app is ready.
        This ensures that signal handlers are connected properly.
        """
        try:
            import elibrary.signals
        except ImportError:
            pass