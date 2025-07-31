from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'
    
    def ready(self):
        import account.signals.payment_signals
        import account.signals.send_invoice_signals
        import account.signals.incoming_invoice_signals
        import account.signals.proforma_invoice_signals
        import account.signals.commerical_invoice_signals
        import account.signals.process_signals
