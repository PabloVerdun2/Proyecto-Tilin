import json
from functools import wraps

from django.http import JsonResponse

from . import almacen
from .validaciones import validar_reserva

# ==============================
# ENDPOINTS DE RESERVAS
# ==============================
#  GET  /api/reservas/        -> 200 listado
#  POST /api/reservas/        -> 201 reserva creada | 400 datos invalidos
#  GET  /api/reservas/<id>/   -> 200 una reserva    | 404 no existe
# Todos requieren sesion iniciada (401 si no la hay). El POST ademas
# necesita el token CSRF en el encabezado X-CSRFToken.


def _error(mensaje, status, **extra):
    return JsonResponse(dict({'error': mensaje}, **extra), status=status)


def _metodo_no_permitido(permitidos):
    respuesta = _error('Metodo no permitido.', 405, permitidos=permitidos)
    respuesta['Allow'] = ', '.join(permitidos)
    return respuesta


def sesion_requerida(vista):
    """Como @login_required, pero responde 401 en JSON en vez de redirigir al login."""
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _error('Debes iniciar sesion.', 401)
        return vista(request, *args, **kwargs)
    return envoltura


# GET y POST /api/reservas/
@sesion_requerida
def reservas(request):
    if request.method == 'GET':
        return JsonResponse({'reservas': almacen.listar()})
    if request.method == 'POST':
        return _crear_reserva(request)
    return _metodo_no_permitido(['GET', 'POST'])


def _crear_reserva(request):
    try:
        datos = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return _error('El cuerpo de la solicitud debe ser JSON valido.', 400)

    if not isinstance(datos, dict):
        return _error('Se esperaba un objeto JSON con los datos de la reserva.', 400)

    limpio, errores = validar_reserva(datos)
    if errores:
        return _error('Datos invalidos.', 400, errores=errores)

    nueva = almacen.crear(limpio)
    return JsonResponse({'reserva': nueva}, status=201)


# GET /api/reservas/<id>/
@sesion_requerida
def reserva_detalle(request, reserva_id):
    if request.method != 'GET':
        return _metodo_no_permitido(['GET'])

    reserva = almacen.obtener(reserva_id)
    if reserva is None:
        return _error('No existe la reserva #%d.' % reserva_id, 404)
    return JsonResponse({'reserva': reserva})
