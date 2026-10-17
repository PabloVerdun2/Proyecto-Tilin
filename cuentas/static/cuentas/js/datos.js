/* ============================================================
   CAPA DE DATOS DE RESERVAS
   ------------------------------------------------------------
   Las reservas llegan del servidor por GET (el fetch esta en
   reservas-lista.js) y las nuevas se crean por POST desde el
   formulario (reserva-form.js), asi que viven en el backend.
   Solo los cambios de estado siguen en localStorage porque
   todavia no tienen endpoint propio.
   ============================================================ */

const ReservasStore = (function () {
    'use strict';

    const CLAVE_ESTADOS = 'gourmet_reservas_estados';

    // Reservas recibidas de la API en la ultima consulta.
    let delServidor = [];

    function leer(clave, porDefecto) {
        try {
            const guardado = localStorage.getItem(clave);
            return guardado === null ? porDefecto : JSON.parse(guardado);
        } catch (e) {
            // localStorage puede fallar en modo privado.
            console.warn('No se pudo leer localStorage.', e);
            return porDefecto;
        }
    }

    function guardar(clave, valor) {
        try {
            localStorage.setItem(clave, JSON.stringify(valor));
        } catch (e) {
            console.warn('No se pudo guardar en localStorage.', e);
        }
    }

    // Reservas del servidor, cada una con el ultimo estado que se le
    // asigno desde el listado.
    function listar() {
        const estados = leer(CLAVE_ESTADOS, {});
        return delServidor.map(function (r) {
            return Object.assign({}, r, { estado: estados[r.id] || r.estado });
        });
    }

    return {
        listar: listar,

        // Recibe el arreglo de reservas que devolvio la API.
        recibir: function (reservas) {
            delServidor = reservas;
        },

        cambiarEstado: function (id, estado) {
            const estados = leer(CLAVE_ESTADOS, {});
            estados[id] = estado;
            guardar(CLAVE_ESTADOS, estados);
            return listar().find(r => r.id === id) || null;
        },

        contar: function () {
            const lista = listar();
            return {
                total: lista.length,
                pendiente: lista.filter(r => r.estado === 'pendiente').length,
                confirmada: lista.filter(r => r.estado === 'confirmada').length,
                cancelada: lista.filter(r => r.estado === 'cancelada').length
            };
        }
    };
})();
