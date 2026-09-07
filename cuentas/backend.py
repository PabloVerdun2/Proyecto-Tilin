from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class EmailBackend(ModelBackend):
    """Autentica con el correo electronico en lugar del username."""

    def authenticate(self, request, username=None, email=None, password=None, **kwargs):
        UserModel = get_user_model()

        # El formulario propio manda 'email'; el admin de Django manda 'username'.
        correo = email or username or kwargs.get(UserModel.USERNAME_FIELD)
        if correo is None or password is None:
            return None

        try:
            user = UserModel.objects.get(email__iexact=correo)
        except UserModel.DoesNotExist:
            # Se calcula un hash igual que si el usuario existiera para que el
            # tiempo de respuesta no revele si el correo esta registrado.
            UserModel().set_password(password)
            return None

        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
