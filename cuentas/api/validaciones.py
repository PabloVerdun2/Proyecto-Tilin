import re
from datetime import date, datetime

from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from ..models import Reserva

# ==============================
# VALIDACION DEL POST /api/reservas/
# ==============================
# Mismas reglas que reserva-form.js: el frontend avisa antes de enviar,
# pero el backend vuelve a validar porque cualquiera puede llamar a la
# API sin pasar por el formulario (Postman, curl, consola, etc.).

RE_TELEFONO = re.compile(r'^\+?[0-9\s-]{7,20}$')
MOTIVOS = [clave for clave, _ in Reserva.OPCIONES_MOTIVO]

# Horario del local: (desde, hasta) segun el dia.
HORARIO_SEMANA = ('12:00', '23:00', 'de 12:00 a 23:00')
HORARIO_FINDE = ('11:00', '23:59', 'de 11:00 a 00:00')


def _texto(datos, campo):
    """Devuelve el campo como texto sin espacios extremos ('' si falta)."""
    valor = datos.get(campo)
    if valor is None:
        return ''
    if not isinstance(valor, str):
        return None   # Tipo invalido: lo reporta quien llama.
    return valor.strip()


def validar_reserva(datos):
    """Devuelve (reserva_limpia, errores). Si errores no esta vacio, no se crea."""
    errores = {}
    limpio = {}

    # Nombre: obligatorio, 3 a 100 caracteres.
    nombre = _texto(datos, 'nombre')
    if nombre is None:
        errores['nombre'] = 'El nombre debe ser texto.'
    elif not nombre:
        errores['nombre'] = 'El nombre es obligatorio.'
    elif len(nombre) < 3:
        errores['nombre'] = 'El nombre debe tener al menos 3 caracteres.'
    elif len(nombre) > 100:
        errores['nombre'] = 'El nombre no puede superar los 100 caracteres.'
    limpio['nombre'] = nombre

    # Correo: obligatorio + formato.
    correo = _texto(datos, 'correo')
    if correo is None:
        errores['correo'] = 'El correo debe ser texto.'
    elif not correo:
        errores['correo'] = 'El correo es obligatorio.'
    else:
        try:
            validate_email(correo)
        except ValidationError:
            errores['correo'] = 'El correo no tiene un formato valido.'
    limpio['correo'] = correo

    # Telefono: obligatorio, solo numeros, espacios y guiones.
    telefono = _texto(datos, 'telefono')
    if telefono is None:
        errores['telefono'] = 'El telefono debe ser texto.'
    elif not telefono:
        errores['telefono'] = 'El telefono es obligatorio.'
    elif not RE_TELEFONO.match(telefono):
        errores['telefono'] = 'El telefono solo admite numeros, espacios y guiones (7 a 20).'
    limpio['telefono'] = telefono

    # Fecha: obligatoria, formato AAAA-MM-DD, no anterior a hoy.
    fecha_texto = _texto(datos, 'fecha')
    fecha = None
    if not fecha_texto:
        errores['fecha'] = 'La fecha es obligatoria (formato AAAA-MM-DD).'
    else:
        try:
            fecha = datetime.strptime(fecha_texto, '%Y-%m-%d').date()
            if fecha < date.today():
                errores['fecha'] = 'La fecha no puede ser anterior a hoy.'
        except ValueError:
            errores['fecha'] = 'La fecha debe tener el formato AAAA-MM-DD.'
    limpio['fecha'] = fecha_texto

    # Hora: obligatoria, formato HH:MM, dentro del horario de ese dia.
    hora_texto = _texto(datos, 'hora')
    if not hora_texto:
        errores['hora'] = 'La hora es obligatoria (formato HH:MM).'
    else:
        try:
            hora_texto = datetime.strptime(hora_texto, '%H:%M').strftime('%H:%M')
            if fecha and 'fecha' not in errores:
                desde, hasta, texto = HORARIO_FINDE if fecha.weekday() >= 5 else HORARIO_SEMANA
                if not desde <= hora_texto <= hasta:
                    errores['hora'] = 'Ese dia atendemos ' + texto + '.'
        except ValueError:
            errores['hora'] = 'La hora debe tener el formato HH:MM.'
    limpio['hora'] = hora_texto

    # Personas: obligatoria, numero entero mayor a cero.
    personas = datos.get('personas')
    if personas in (None, ''):
        errores['personas'] = 'La cantidad de personas es obligatoria.'
    else:
        try:
            # bool es subclase de int: true/false no cuentan como numero.
            if isinstance(personas, bool):
                raise ValueError
            personas = int(personas)
            if personas < 1:
                raise ValueError
        except (TypeError, ValueError):
            errores['personas'] = 'La cantidad de personas debe ser un numero mayor a cero.'
    limpio['personas'] = personas

    # Motivo: opcional (por defecto 'cena'), debe ser una opcion conocida.
    motivo = _texto(datos, 'motivo')
    if motivo is None or (motivo and motivo not in MOTIVOS):
        errores['motivo'] = 'El motivo debe ser uno de: ' + ', '.join(MOTIVOS) + '.'
    limpio['motivo'] = motivo or 'cena'

    # Notas: opcionales, hasta 500 caracteres.
    notas = _texto(datos, 'notas')
    if notas is None:
        errores['notas'] = 'Las notas deben ser texto.'
    elif len(notas) > 500:
        errores['notas'] = 'Las notas no pueden superar los 500 caracteres.'
    limpio['notas'] = notas

    return limpio, errores
