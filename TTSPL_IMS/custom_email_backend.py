from django.core.mail.backends.smtp import EmailBackend as BaseEmailBackend
from django.conf import settings
from  TTSPL_IMS_App.models import SecondaryEmailConfig  # Import your model

class CustomEmailBackend(BaseEmailBackend):
    def __init__(self, *args, **kwargs):
        use_secondary = kwargs.pop('use_secondary', False)

        if use_secondary:
            try:
                # Fetch the latest secondary email configuration from the database
                secondary_config = SecondaryEmailConfig.objects.latest('id')
                self.email_host = secondary_config.host
                self.email_port = secondary_config.port
                self.use_tls = secondary_config.use_tls
                self.username = secondary_config.host_user
                self.password = secondary_config.host_password
                self.default_from_email = secondary_config.default_from_email
            except SecondaryEmailConfig.DoesNotExist:
                raise Exception("Secondary email configuration not found.")
        else:
            self.email_host = settings.EMAIL_HOST
            self.email_port = settings.EMAIL_PORT
            self.use_tls = settings.EMAIL_USE_TLS
            self.username = settings.EMAIL_HOST_USER
            self.password = settings.EMAIL_HOST_PASSWORD
            self.default_from_email = settings.DEFAULT_FROM_EMAIL

        super().__init__(email_host=self.email_host,
                         email_port=self.email_port,
                         use_tls=self.use_tls,
                         username=self.username,
                         password=self.password,
                         *args, **kwargs)
