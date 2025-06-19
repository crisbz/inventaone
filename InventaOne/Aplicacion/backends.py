from django.contrib.auth.backends import ModelBackend
from .models import Usuario

class EmailBackend(ModelBackend):
    """
    Permite autenticación usando el campo 'correo' en vez de 'username'.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = Usuario.objects.get(email=username)
        except Usuario.DoesNotExist:
            return None
        if user.check_password(password):
            return user
        return None