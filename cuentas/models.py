from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# ==============================
# MODELO CUSTOMUSER
# ==============================
class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    OPCIONES_ROL = [
        ('cliente', 'Cliente'),
        ('recepcionista', 'Recepcionista'),
        ('admin', 'Administrador'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    rol = models.CharField(max_length=20, choices=OPCIONES_ROL, default='cliente')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

# ==============================
# MODELO MESA
# ==============================
class Mesa(models.Model):
    numero = models.IntegerField(unique=True)
    capacidad = models.IntegerField()
    disponible = models.BooleanField(default=True)

    def __str__(self):
        return f"Mesa {self.numero} - {'Disponible' if self.disponible else 'Ocupada'}"

# ==============================
# MODELO RESERVA
# ==============================
class Reserva(models.Model):
    OPCIONES_MOTIVO = [
        ('cena', 'Cena normal'),
        ('birthday', 'Cumpleaños'),
        ('anniversary', 'Aniversario'),
        ('business', 'Reunión de negocios'),
        ('babyshower', 'Baby Shower'),
        ('other', 'Otro evento especial'),
    ]

    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    mesa = models.ForeignKey(Mesa, on_delete=models.SET_NULL, null=True)
    fecha = models.DateField()
    hora = models.TimeField()
    cantidad_personas = models.PositiveIntegerField()
    motivo = models.CharField(max_length=20, choices=OPCIONES_MOTIVO, default='cena')
    nombre_contacto = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    notas_adicionales = models.TextField(blank=True)
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f"Reserva de {self.cliente.email} el {self.fecha} a las {self.hora}"


# ==============================
# MODELO COMIDA
# ==============================
class Comida(models.Model):
    nombre = models.CharField(max_length=100)
    precio = models.IntegerField(help_text="Precio en guaranies")

    class Meta:
        verbose_name_plural = "Comidas"
        ordering = ['nombre']

    @property
    def precio_formateado(self):
        """Precio con punto como separador de miles: 50000 -> '50.000'."""
        return f"{self.precio:,}".replace(",", ".")

    def __str__(self):
        return f"{self.nombre} - {self.precio_formateado} gs"
