/* ============================================================
   CAPA DE DATOS DE RESERVAS
   ------------------------------------------------------------
   Indicador 3: las reservas ya no estan escritas aca, llegan del
   servidor por GET (el fetch esta en reservas-lista.js).
   Lo que todavia no tiene endpoint propio sigue en localStorage
   hasta la proxima etapa: las reservas creadas en el formulario
   (futuro POST) y los cambios de estado.
   ============================================================ */

const ReservasStore = (function () {
    'use strict';

    const CLAVE_NUEVAS  = 'gourmet_reservas_nuevas';
    const CLAVE_ESTADOS = 'gourmet_reservas_estados';

    // Las reservas locales se numeran desde 1001 para no repetir un id
    // del servidor. Con el POST real, el id lo va a asignar el backend.
    const PRIMER_ID_LOCAL = 1001;

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

    // Reservas del servidor + las creadas en el formulario, cada una con
    // el ultimo estado que se le asigno desde el listado.
    function listar() {
        const estados = leer(CLAVE_ESTADOS, {});
        return delServidor.concat(leer(CLAVE_NUEVAS, [])).map(function (r) {
            return Object.assign({}, r, { estado: estados[r.id] || r.estado });
        });
    }

    return {
        listar: listar,

        // Recibe el arreglo de reservas que devolvio la API.
        recibir: function (reservas) {
            delServidor = reservas;
        },

        agregar: function (datos) {
            const nuevas = leer(CLAVE_NUEVAS, []);
            const ultimoId = nuevas.reduce((max, r) => Math.max(max, r.id), PRIMER_ID_LOCAL - 1);
            const nueva = Object.assign({}, datos, {
                id: ultimoId + 1,
                estado: 'pendiente'
            });
            nuevas.push(nueva);
            guardar(CLAVE_NUEVAS, nuevas);
            return nueva;
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
