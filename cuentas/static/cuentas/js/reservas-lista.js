/* ============================================================
   LISTADO DE RESERVAS
   ------------------------------------------------------------
   Interacciones del punto 3.7: mostrar el listado, filtrarlo,
   cambiar el estado de una reserva y actualizar los contadores,
   todo sin recargar la pagina.
   ============================================================ */

(function () {
    'use strict';

    const contenedor = document.getElementById('lista-reservas');
    if (!contenedor) return;   // Esta pantalla no es la del listado.

    const filtroEstado = document.getElementById('filtro-estado');
    const filtroTexto  = document.getElementById('filtro-texto');
    const contadores   = document.getElementById('contadores');

    const MOTIVOS = {
        cena: 'Cena normal',
        birthday: 'Cumpleanos',
        anniversary: 'Aniversario',
        business: 'Reunion de negocios',
        babyshower: 'Baby Shower',
        other: 'Otro evento especial'
    };

    const ETIQUETA_ESTADO = {
        pendiente: 'Pendiente',
        confirmada: 'Confirmada',
        cancelada: 'Cancelada'
    };

    function escapar(texto) {
        const d = document.createElement('div');
        d.textContent = texto === null || texto === undefined ? '' : String(texto);
        return d.innerHTML;
    }

    /* ---------- Filtrado ---------- */
    function filtrar(lista) {
        const estado = filtroEstado ? filtroEstado.value : 'todas';
        const texto = filtroTexto ? filtroTexto.value.trim().toLowerCase() : '';

        return lista.filter(function (r) {
            const coincideEstado = (estado === 'todas') || (r.estado === estado);
            const coincideTexto = (texto === '') ||
                r.nombre.toLowerCase().includes(texto) ||
                r.correo.toLowerCase().includes(texto);
            return coincideEstado && coincideTexto;
        });
    }

    /* ---------- Botones segun el estado actual ---------- */
    function acciones(r) {
        if (r.estado === 'pendiente') {
            return '<button class="btn-accion btn-confirmar" data-id="' + r.id + '" data-estado="confirmada">Confirmar</button>' +
                   '<button class="btn-accion btn-cancelar" data-id="' + r.id + '" data-estado="cancelada">Cancelar</button>';
        }
        if (r.estado === 'confirmada') {
            return '<button class="btn-accion btn-cancelar" data-id="' + r.id + '" data-estado="cancelada">Cancelar</button>';
        }
        return '<button class="btn-accion btn-reabrir" data-id="' + r.id + '" data-estado="pendiente">Reabrir</button>';
    }

    function tarjeta(r) {
        return '' +
            '<article class="reserva-item estado-' + r.estado + '" data-id="' + r.id + '">' +
                '<div class="reserva-cabecera">' +
                    '<h3>#' + r.id + ' &middot; ' + escapar(r.nombre) + '</h3>' +
                    '<span class="badge badge-' + r.estado + '">' + ETIQUETA_ESTADO[r.estado] + '</span>' +
                '</div>' +
                '<ul class="reserva-datos">' +
                    '<li><strong>Fecha:</strong> ' + escapar(r.fecha) + ' a las ' + escapar(r.hora) + '</li>' +
                    '<li><strong>Personas:</strong> ' + escapar(r.personas) + '</li>' +
                    '<li><strong>Motivo:</strong> ' + escapar(MOTIVOS[r.motivo] || 'Cena normal') + '</li>' +
                    '<li><strong>Contacto:</strong> ' + escapar(r.correo) + ' &middot; ' + escapar(r.telefono) + '</li>' +
                    (r.notas ? '<li><strong>Notas:</strong> ' + escapar(r.notas) + '</li>' : '') +
                '</ul>' +
                '<div class="reserva-acciones">' + acciones(r) + '</div>' +
            '</article>';
    }

    function pintarContadores() {
        if (!contadores) return;
        const c = ReservasStore.contar();
        contadores.innerHTML =
            '<span class="contador"><strong>' + c.total + '</strong> en total</span>' +
            '<span class="contador contador-pendiente"><strong>' + c.pendiente + '</strong> pendientes</span>' +
            '<span class="contador contador-confirmada"><strong>' + c.confirmada + '</strong> confirmadas</span>' +
            '<span class="contador contador-cancelada"><strong>' + c.cancelada + '</strong> canceladas</span>';
    }

    function render() {
        const visibles = filtrar(ReservasStore.listar());

        if (visibles.length === 0) {
            contenedor.innerHTML =
                '<p class="sin-resultados">No hay reservas que coincidan con el filtro.</p>';
        } else {
            // Las mas proximas primero.
            visibles.sort(function (a, b) {
                return (a.fecha + a.hora).localeCompare(b.fecha + b.hora);
            });
            contenedor.innerHTML = visibles.map(tarjeta).join('');
        }
        pintarContadores();
    }

    /* ---------- Eventos ---------- */
    contenedor.addEventListener('click', function (evento) {
        const boton = evento.target.closest('.btn-accion');
        if (!boton) return;
        ReservasStore.cambiarEstado(parseInt(boton.dataset.id, 10), boton.dataset.estado);
        render();
    });

    if (filtroEstado) filtroEstado.addEventListener('change', render);
    if (filtroTexto)  filtroTexto.addEventListener('input', render);

    render();
})();
