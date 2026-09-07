from django.shortcuts import render, redirect
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
# El listado se arma del lado cliente con datos simulados: en esta etapa
# del MVP la vista solo entrega la pantalla.
@login_required
def reservas_view(request):
    return render(request, 'cuentas/reservas.html', {'usuario': request.user.first_name})

# LOGOUT
def logout_view(request):
    logout(request)
    return redirect('login')
