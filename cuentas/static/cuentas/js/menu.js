/* ============================================================
   MENU: BUSQUEDA Y ORDENAMIENTO
   ------------------------------------------------------------
   Los platos los renderiza Django desde el modelo Comida; este
   archivo solo agrega la interaccion (punto 3.7: filtrar
   registros y actualizar el listado en pantalla).
   ============================================================ */

(function () {
    'use strict';

    const grilla = document.getElementById('grilla-platos');
    if (!grilla) return;

    const buscador = document.getElementById('buscar-plato');
    const orden    = document.getElementById('orden-plato');
    const resumen  = document.getElementById('resumen-platos');

    const platos = Array.from(grilla.querySelectorAll('.menu-item'));

    function aplicar() {
        const texto = buscador ? buscador.value.trim().toLowerCase() : '';

        // Filtrar: se muestran solo los platos cuyo nombre coincide.
        let visibles = 0;
        platos.forEach(function (el) {
            const coincide = el.dataset.nombre.toLowerCase().includes(texto);
            el.hidden = !coincide;
            if (coincide) visibles++;
        });

        // Ordenar: se reubican los nodos segun el criterio elegido.
        const criterio = orden ? orden.value : 'nombre';
        const ordenados = platos.slice().sort(function (a, b) {
            if (criterio === 'precio-asc')  return a.dataset.precio - b.dataset.precio;
            if (criterio === 'precio-desc') return b.dataset.precio - a.dataset.precio;
            return a.dataset.nombre.localeCompare(b.dataset.nombre, 'es');
        });
        ordenados.forEach(el => grilla.appendChild(el));

        if (resumen) {
            resumen.textContent = visibles === platos.length
                ? 'Mostrando los ' + platos.length + ' platos de la carta.'
                : 'Mostrando ' + visibles + ' de ' + platos.length + ' platos.';
        }
    }

    if (buscador) buscador.addEventListener('input', aplicar);
    if (orden)    orden.addEventListener('change', aplicar);

    aplicar();
})();
