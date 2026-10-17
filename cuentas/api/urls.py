from django.urls import path

from . import views

# Rutas de la API, montadas bajo /api/ en cuentas/urls.py.
urlpatterns = [
    path('reservas/', views.reservas, name='reservas_api'),
    path('reservas/<int:reserva_id>/', views.reserva_detalle, name='reserva_detalle_api'),
]
