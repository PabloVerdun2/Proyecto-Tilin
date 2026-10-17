import threading

# ==============================
# ALMACEN TEMPORAL DE RESERVAS
# ==============================
# El Indicador 4 todavia no exige base de datos: las reservas viven en
# una lista en memoria. NO son persistentes, se pierden al reiniciar el
# servidor. En la proxima etapa estas funciones pasan a usar el modelo
# Reserva y las vistas de la API no cambian.

_reservas = [
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
_siguiente_id = 4

# El servidor de desarrollo atiende varias solicitudes a la vez: el lock
# evita que dos POST simultaneos reciban el mismo id.
_lock = threading.Lock()


def listar():
    with _lock:
        return [dict(r) for r in _reservas]


def obtener(reserva_id):
    with _lock:
        for r in _reservas:
            if r['id'] == reserva_id:
                return dict(r)
    return None


def crear(datos):
    """Agrega una reserva ya validada; el id y el estado los asigna el servidor."""
    global _siguiente_id
    with _lock:
        nueva = dict(datos, id=_siguiente_id, estado='pendiente')
        _reservas.append(nueva)
        _siguiente_id += 1
        return dict(nueva)
