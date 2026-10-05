from django.urls import path
from .views import (
    login_view,
    logout_view,
    register_view,
    index_view,
    menu_view,
    reservas_view,
    reservas_api
)

urlpatterns = [
    path('', index_view, name='inicio'),            # Página principal (requiere login)
    path('login/', login_view, name='login'),       # Formulario de login
    path('logout/', logout_view, name='logout'),    # Cerrar sesión
    path('register/', register_view, name='register'),  # Registro de nuevos usuarios
    path('menu/', menu_view, name='menu'),          # Menu del restaurante
    path('reservas/', reservas_view, name='reservas'),  # Listado de reservas
    path('api/reservas/', reservas_api, name='reservas_api'),  # Reservas en JSON
]
