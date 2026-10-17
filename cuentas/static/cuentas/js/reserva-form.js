/* ============================================================
   FORMULARIO DE RESERVA: VALIDACIONES DEL LADO CLIENTE
   ------------------------------------------------------------
   Validaciones exigidas por el Indicador 2 (punto 3.5):
   obligatorios, formato de correo, valores numericos, fechas
   validas, longitud minima/maxima y mensajes claros.

   Indicador 4: si los datos son validos se envian por POST a la
   API propia (/api/reservas/), que vuelve a validarlos.
   ============================================================ */

(function () {
    'use strict';

    const form = document.getElementById('form-reserva');
    if (!form) return;   // Esta pantalla no tiene el formulario.

    const RE_CORREO = /^[^\s@]+@[^\s@]+\.[a-z]{2,}$/i;
    const RE_TELEFONO = /^\+?[0-9\s-]{7,20}$/;

    // Horario del local, tal como figura en el pie de pagina.
    const HORARIOS = {
        semana: { desde: '12:00', hasta: '23:00', texto: 'de 12:00 a 23:00' },
        finde:  { desde: '11:00', hasta: '23:59', texto: 'de 11:00 a 00:00' }
    };

    function horarioDe(fechaTexto) {
        // 'T00:00:00' evita que el navegador interprete la fecha como UTC.
        const dia = new Date(fechaTexto + 'T00:00:00').getDay();
        return (dia === 0 || dia === 6) ? HORARIOS.finde : HORARIOS.semana;
    }

    function hoyTexto() {
        const h = new Date();
        const mes = String(h.getMonth() + 1).padStart(2, '0');
        const dia = String(h.getDate()).padStart(2, '0');
        return h.getFullYear() + '-' + mes + '-' + dia;
    }

    /* ---------- Reglas de validacion ---------- */
    function validar(d) {
        const errores = {};

        // Nombre: obligatorio + longitud minima y maxima.
        if (!d.nombre) {
            errores.name = 'Ingresa el nombre de quien reserva.';
        } else if (d.nombre.length < 3) {
            errores.name = 'El nombre debe tener al menos 3 caracteres.';
        } else if (d.nombre.length > 100) {
            errores.name = 'El nombre no puede superar los 100 caracteres.';
        }

        // Correo: obligatorio + formato.
        if (!d.correo) {
            errores.email = 'Ingresa un correo de contacto.';
        } else if (!RE_CORREO.test(d.correo)) {
            errores.email = 'El correo no tiene un formato valido (ejemplo: nombre@dominio.com).';
        }

        // Telefono: obligatorio + solo numeros.
        if (!d.telefono) {
            errores.phone = 'Ingresa un telefono de contacto.';
        } else if (!RE_TELEFONO.test(d.telefono)) {
            errores.phone = 'El telefono solo admite numeros, espacios y guiones (7 a 20 digitos).';
        }

        // Fecha: obligatoria + no puede ser anterior a hoy.
        if (!d.fecha) {
            errores.date = 'Elegi la fecha de la reserva.';
        } else if (d.fecha < hoyTexto()) {
            errores.date = 'La fecha no puede ser anterior a hoy.';
        }

        // Hora: obligatoria + dentro del horario de atencion de ese dia.
        if (!d.hora) {
            errores.time = 'Elegi la hora de la reserva.';
        } else if (d.fecha && !errores.date) {
            const h = horarioDe(d.fecha);
            if (d.hora < h.desde || d.hora > h.hasta) {
                errores.time = 'Ese dia atendemos ' + h.texto + '.';
            }
        }

        // Cantidad de personas: obligatoria + numerica.
        const personas = parseInt(d.personas, 10);
        if (!d.personas) {
            errores.guests = 'Indica para cuantas personas es la reserva.';
        } else if (isNaN(personas) || personas < 1) {
            errores.guests = 'La cantidad de personas debe ser un numero mayor a cero.';
        }

        return errores;
    }

    /* ---------- Mostrar y limpiar mensajes ---------- */
    function limpiarErrores() {
        form.querySelectorAll('.error-campo').forEach(e => e.remove());
        form.querySelectorAll('.campo-invalido').forEach(e => e.classList.remove('campo-invalido'));
    }

    function mostrarErrores(errores) {
        Object.keys(errores).forEach(function (campo) {
            const input = form.querySelector('[name="' + campo + '"]');
            if (!input) return;
            input.classList.add('campo-invalido');
            const aviso = document.createElement('span');
            aviso.className = 'error-campo';
            aviso.textContent = errores[campo];
            input.parentNode.appendChild(aviso);
        });
        // Lleva el foco al primer campo con problema.
        const primero = form.querySelector('.campo-invalido');
        if (primero) primero.focus();
    }

    function mostrarExito(reserva) {
        const aviso = document.createElement('div');
        aviso.id = 'aviso-exito';
        aviso.className = 'aviso-exito';
        aviso.innerHTML =
            '<strong>Reserva registrada.</strong> ' +
            'Numero #' + reserva.id + ' para ' + reserva.personas + ' persona(s) ' +
            'el ' + reserva.fecha + ' a las ' + reserva.hora + '. ' +
            'Queda en estado <em>pendiente</em>. ' +
            '<a href="' + form.dataset.urlReservas + '">Ver mis reservas</a>';
        form.parentNode.insertBefore(aviso, form);
        aviso.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    function quitarAvisos() {
        ['aviso-exito', 'aviso-envio-error'].forEach(function (id) {
            const previo = document.getElementById(id);
            if (previo) previo.remove();
        });
    }

    function mostrarErrorEnvio(mensaje) {
        const aviso = document.createElement('div');
        aviso.id = 'aviso-envio-error';
        aviso.className = 'aviso-envio-error';
        aviso.textContent = mensaje;
        form.parentNode.insertBefore(aviso, form);
        aviso.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    /* ---------- Envio a la API (POST) ---------- */
    // La API nombra los campos en espanol; el formulario, en ingles.
    const CAMPO_FORM = {
        fecha: 'date', hora: 'time', personas: 'guests', motivo: 'occasion',
        nombre: 'name', correo: 'email', telefono: 'phone', notas: 'notes'
    };

    const boton = form.querySelector('[type="submit"]');

    function enviar(datos) {
        boton.disabled = true;

        fetch(form.dataset.urlApi, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // Django rechaza un POST sin el token CSRF (403).
                'X-CSRFToken': form.querySelector('[name="csrfmiddlewaretoken"]').value
            },
            body: JSON.stringify(datos)
        })
            .then(function (response) {
                return response.json()
                    .catch(function () { return {}; })   // Respuesta sin JSON.
                    .then(function (cuerpo) {
                        return { status: response.status, cuerpo: cuerpo };
                    });
            })
            .then(function (r) {
                if (r.status === 201) {
                    form.reset();
                    mostrarExito(r.cuerpo.reserva);
                } else if (r.status === 400 && r.cuerpo.errores) {
                    // El backend detecto datos invalidos: se marcan los campos.
                    const errores = {};
                    Object.keys(r.cuerpo.errores).forEach(function (campo) {
                        errores[CAMPO_FORM[campo] || campo] = r.cuerpo.errores[campo];
                    });
                    mostrarErrores(errores);
                } else if (r.status === 401 || r.status === 403) {
                    mostrarErrorEnvio('Tu sesion vencio. Recarga la pagina e inicia sesion de nuevo.');
                } else {
                    mostrarErrorEnvio(r.cuerpo.error || ('El servidor respondio ' + r.status + '.'));
                }
            })
            .catch(function (error) {
                console.error('No se pudo enviar la reserva:', error);
                mostrarErrorEnvio('No se pudo conectar con el servidor. Intenta de nuevo.');
            })
            .finally(function () {
                boton.disabled = false;
            });
    }

    form.addEventListener('submit', function (evento) {
        evento.preventDefault();   // El envio lo hace fetch(), sin recargar.
        limpiarErrores();
        quitarAvisos();

        const datos = {
            fecha:    form.querySelector('[name="date"]').value,
            hora:     form.querySelector('[name="time"]').value,
            personas: form.querySelector('[name="guests"]').value,
            motivo:   form.querySelector('[name="occasion"]').value,
            nombre:   form.querySelector('[name="name"]').value.trim(),
            correo:   form.querySelector('[name="email"]').value.trim(),
            telefono: form.querySelector('[name="phone"]').value.trim(),
            notas:    form.querySelector('[name="notes"]').value.trim()
        };

        const errores = validar(datos);
        if (Object.keys(errores).length > 0) {
            mostrarErrores(errores);
            return;
        }

        datos.personas = parseInt(datos.personas, 10);
        enviar(datos);
    });

    // Al corregir un campo se borra su mensaje de error.
    form.addEventListener('input', function (evento) {
        const campo = evento.target;
        campo.classList.remove('campo-invalido');
        const aviso = campo.parentNode.querySelector('.error-campo');
        if (aviso) aviso.remove();
    });

    // El selector de fecha no deja elegir dias pasados.
    const inputFecha = form.querySelector('[name="date"]');
    if (inputFecha) inputFecha.min = hoyTexto();
})();
