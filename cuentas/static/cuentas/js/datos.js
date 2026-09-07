/* ============================================================
   CAPA DE DATOS SIMULADOS
   ------------------------------------------------------------
   El Indicador 2 no exige backend ni base de datos, asi que las
   reservas del MVP viven en un arreglo de JavaScript que se
   persiste en localStorage. Cuando se conecte el backend real,
   solo hay que reemplazar leer() y guardar() por llamadas fetch().
   ============================================================ */

const ReservasStore = (function () {
    'use strict';

    const CLAVE = 'gourmet_reservas';

    // Datos de ejemplo para que el listado no arranque vacio en la demo.
    const SEMILLA = [
        {
            id: 1, nombre: 'Maria Gonzalez', correo: 'maria@ejemplo.com',
            telefono: '+595981123456', fecha: '2026-09-12', hora: '20:00',
            personas: 4, motivo: 'birthday', notas: 'Mesa cerca de la ventana',
            estado: 'confirmada'
        },
        {
            id: 2, nombre: 'Carlos Benitez', correo: 'carlos@ejemplo.com',
            telefono: '+595971998877', fecha: '2026-09-15', hora: '13:30',
            personas: 2, motivo: 'business', notas: '',
            estado: 'pendiente'
        },
        {
            id: 3, nombre: 'Lucia Ramirez', correo: 'lucia@ejemplo.com',
            telefono: '+595983445566', fecha: '2026-09-18', hora: '21:00',
            personas: 6, motivo: 'anniversary', notas: 'Torta al final',
            estado: 'cancelada'
        }
    ];

    function leer() {
        try {
            const guardado = localStorage.getItem(CLAVE);
            if (guardado === null) {
                guardar(SEMILLA);
                return SEMILLA.slice();
            }
            return JSON.parse(guardado);
        } catch (e) {
            // localStorage puede fallar en modo privado: se sigue con la semilla.
            console.warn('No se pudo leer localStorage, se usan datos de ejemplo.', e);
            return SEMILLA.slice();
        }
    }

    function guardar(lista) {
        try {
            localStorage.setItem(CLAVE, JSON.stringify(lista));
        } catch (e) {
            console.warn('No se pudo guardar en localStorage.', e);
        }
    }

    function siguienteId(lista) {
        return lista.reduce((max, r) => Math.max(max, r.id), 0) + 1;
    }

    return {
        listar: leer,

        agregar: function (datos) {
            const lista = leer();
            const nueva = Object.assign({}, datos, {
                id: siguienteId(lista),
                estado: 'pendiente'
            });
            lista.push(nueva);
            guardar(lista);
            return nueva;
        },

        cambiarEstado: function (id, estado) {
            const lista = leer();
            const reserva = lista.find(r => r.id === id);
            if (!reserva) return null;
            reserva.estado = estado;
            guardar(lista);
            return reserva;
        },

        contar: function () {
            const lista = leer();
            return {
                total: lista.length,
                pendiente: lista.filter(r => r.estado === 'pendiente').length,
                confirmada: lista.filter(r => r.estado === 'confirmada').length,
                cancelada: lista.filter(r => r.estado === 'cancelada').length
            };
        }
    };
})();
