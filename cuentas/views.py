from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from .forms import RegistroUsuarioForm
from .models import Comida

# LOGIN
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, "Correo o contraseña incorrectos.")
    return render(request, 'cuentas/login.html')

# REGISTRO
def register_view(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('inicio')
        else:
            messages.error(request, "Por favor corrige los errores.")
    else:
        form = RegistroUsuarioForm()
    return render(request, 'cuentas/register.html', {'form': form})

# INDEX (requiere login)
@login_required
def index_view(request):
    return render(request, 'cuentas/index.html', {'usuario': request.user.first_name})

# MENU DEL RESTAURANTE (requiere login)
@login_required
def menu_view(request):
    return render(request, 'cuentas/menu.html', {
        'usuario': request.user.first_name,
        'platos': Comida.objects.all(),
    })

# LISTADO DE RESERVAS (requiere login)
# La vista solo entrega la pantalla: las reservas las pide el navegador
# con fetch() a reservas_api.
@login_required
def reservas_view(request):
    return render(request, 'cuentas/reservas.html', {'usuario': request.user.first_name})

# Reservas que devuelve la API. El Indicador 3 todavia no exige base de
# datos, asi que son datos fijos: en la proxima etapa se reemplazan por
# una consulta al modelo Reserva.
RESERVAS_EJEMPLO = [
    {
        'id': 1, 'nombre': 'Maria Gonzalez', 'correo': 'maria@ejemplo.com',
        'telefono': '+595981123456', 'fecha': '2026-09-12', 'hora': '20:00',
        'personas': 4, 'motivo': 'birthday', 'notas': 'Mesa cerca de la ventana',
        'estado': 'confirmada',
    },
    {
        'id': 2, 'nombre': 'Carlos Benitez', 'correo': 'carlos@ejemplo.com',
        'telefono': '+595971998877', 'fecha': '2026-09-15', 'hora': '13:30',
        'personas': 2, 'motivo': 'business', 'notas': '',
        'estado': 'pendiente',
    },
    {
        'id': 3, 'nombre': 'Lucia Ramirez', 'correo': 'lucia@ejemplo.com',
        'telefono': '+595983445566', 'fecha': '2026-09-18', 'hora': '21:00',
        'personas': 6, 'motivo': 'anniversary', 'notas': 'Torta al final',
        'estado': 'cancelada',
    },
]

# API: GET /api/reservas/ (requiere login)
# Responde JSON con la forma {"reservas": [ {...}, {...} ]}.
@login_required
def reservas_api(request):
    return JsonResponse({'reservas': RESERVAS_EJEMPLO})

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')
