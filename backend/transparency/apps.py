from django.apps import AppConfig

class TransparencyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transparency'
    verbose_name = 'Financial Transparency & Governance'
    
    def ready(self):
        import transparency.signals