import json
from functools import wraps

from django.http import JsonResponse

from ..models import Reserva
from .validaciones import validar_reserva

# Endpoints de reservas (persisten en la base de datos):
#   GET  /api/reservas/       -> 200 listado
#   POST /api/reservas/       -> 201 creada | 400 datos invalidos
#   GET  /api/reservas/<id>/  -> 200 una reserva | 404 no existe
# Requieren sesion iniciada (401). El POST necesita el token CSRF.


def _error(mensaje, status, **extra):
    return JsonResponse(dict({'error': mensaje}, **extra), status=status)


def _metodo_no_permitido(permitidos):
    respuesta = _error('Metodo no permitido.', 405, permitidos=permitidos)
    respuesta['Allow'] = ', '.join(permitidos)
    return respuesta


def _serializar(reserva):
    return {
        'id': reserva.id,
        'nombre': reserva.nombre_contacto,
        'correo': reserva.correo,
        'telefono': reserva.telefono,
        'fecha': reserva.fecha.isoformat(),
        'hora': reserva.hora.strftime('%H:%M'),
        'personas': reserva.cantidad_personas,
        'motivo': reserva.motivo,
        'notas': reserva.notas_adicionales,
        'estado': reserva.estado,
    }


def sesion_requerida(vista):
    # Como @login_required, pero responde 401 en JSON en vez de redirigir.
    @wraps(vista)
    def envoltura(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return _error('Debes iniciar sesion.', 401)
        return vista(request, *args, **kwargs)
    return envoltura


@sesion_requerida
def reservas(request):
    if request.method == 'GET':
        lista = [_serializar(r) for r in Reserva.objects.all()]
        return JsonResponse({'reservas': lista})
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

    # CREATE: guarda en la BD, asociada al usuario autenticado.
    reserva = Reserva.objects.create(
        cliente=request.user,
        nombre_contacto=limpio['nombre'],
        correo=limpio['correo'],
        telefono=limpio['telefono'],
        fecha=limpio['fecha'],
        hora=limpio['hora'],
        cantidad_personas=limpio['personas'],
        motivo=limpio['motivo'],
        notas_adicionales=limpio['notas'],
    )
    return JsonResponse({'reserva': _serializar(reserva)}, status=201)


@sesion_requerida
def reserva_detalle(request, reserva_id):
    if request.method != 'GET':
        return _metodo_no_permitido(['GET'])

    reserva = Reserva.objects.filter(pk=reserva_id).first()
    if reserva is None:
        return _error('No existe la reserva #%d.' % reserva_id, 404)
    return JsonResponse({'reserva': _serializar(reserva)})
