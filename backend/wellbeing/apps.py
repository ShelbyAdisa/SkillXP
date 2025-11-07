from django.apps import AppConfig

class WellbeingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wellbeing'
    verbose_name = 'Wellbeing Management'
    
    def ready(self):
        import wellbeing.signals