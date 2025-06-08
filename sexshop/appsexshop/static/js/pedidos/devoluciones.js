document.addEventListener('DOMContentLoaded', function() {
    // Elementos DOM
    const btnSolicitarDevolucion = document.getElementById('btnSolicitarDevolucion');
    const modalDevolucion = new bootstrap.Modal(document.getElementById('modalDevolucion'));
    const modalTerminos = new bootstrap.Modal(document.getElementById('modalTerminos'));
    const modalVerSolicitud = new bootstrap.Modal(document.getElementById('modalVerSolicitud'));
    const formDevolucion = document.getElementById('formDevolucion');
    const enlaceTerminos = document.getElementById('enlaceTerminos');
    const btnAceptarTerminos = document.getElementById('btnAceptarTerminos');
    const listaVacia = document.getElementById('listaVacia');
    const listaDevoluciones = document.getElementById('listaDevoluciones');
    const selectPedido = document.getElementById('pedido');
    const selectProductos = document.getElementById('productos');
    
    // Variables globales
    let devoluciones = [];
    let ultimaDevolucionTiempo = null;
    
    // Base de datos simulada de productos por pedido
    const productosPorPedido = {
        '1': [
            { id: 101, nombre: 'Smartphone Galaxy S22 - Negro' },
            { id: 102, nombre: 'Funda protectora transparente' },
            { id: 103, nombre: 'Cargador rápido 25W' }
        ],
        '2': [
            { id: 201, nombre: 'Laptop HP Pavilion 15"' },
            { id: 202, nombre: 'Mouse inalámbrico' },
            { id: 203, nombre: 'Mochila para laptop' }
        ],
        '3': [
            { id: 301, nombre: 'Audífonos Sony WH-1000XM4' },
            { id: 302, nombre: 'Cable USB tipo C' },
            { id: 303, nombre: 'Estuche para audífonos' }
        ]
    };
    
    // Funciones de persistencia
    function guardarDevoluciones() {
        try {
            localStorage.setItem('devoluciones', JSON.stringify(devoluciones));
        } catch (error) {
            console.error('Error al guardar devoluciones:', error);
        }
    }
    
    function cargarDevolucionesGuardadas() {
        try {
            const devolucionesGuardadas = localStorage.getItem('devoluciones');
            if (devolucionesGuardadas) {
                devoluciones = JSON.parse(devolucionesGuardadas);
                // Convertir las fechas de string a objeto Date
                devoluciones.forEach(devolucion => {
                    devolucion.fecha = new Date(devolucion.fecha);
                });
            }
        } catch (error) {
            console.error('Error al cargar devoluciones:', error);
            devoluciones = [];
        }
    }
    
    // Event Listeners
    btnSolicitarDevolucion.addEventListener('click', abrirModalDevolucion);
    formDevolucion.addEventListener('submit', procesarDevolucion);
    enlaceTerminos.addEventListener('click', abrirTerminos);
    btnAceptarTerminos.addEventListener('click', aceptarTerminos);
    selectPedido.addEventListener('change', cargarProductos);
    
    // Cargar datos iniciales
    cargarDevolucionesGuardadas(); // Cargar desde localStorage primero
    cargarDevoluciones();
    
    // Funciones
    function abrirModalDevolucion() {
        // Resetear formulario
        formDevolucion.reset();
        formDevolucion.classList.remove('was-validated');
        selectProductos.disabled = true;
        selectProductos.innerHTML = '';
        
        modalDevolucion.show();
    }
    
    function cargarProductos() {
        const pedidoId = selectPedido.value;
        
        // Limpiar y habilitar el select de productos
        selectProductos.innerHTML = '';
        selectProductos.disabled = false;
        
        // Cargar productos del pedido seleccionado
        if (pedidoId && productosPorPedido[pedidoId]) {
            productosPorPedido[pedidoId].forEach(producto => {
                const option = document.createElement('option');
                option.value = producto.id;
                option.textContent = producto.nombre;
                selectProductos.appendChild(option);
            });
        }
    }
    
    function abrirTerminos(e) {
        e.preventDefault();
        modalTerminos.show();
    }
    
    function aceptarTerminos() {
        document.getElementById('terminos').checked = true;
        modalTerminos.hide();
    }
    
    function procesarDevolucion(e) {
        e.preventDefault();
        
        // Validar formulario
        if (!formDevolucion.checkValidity()) {
            e.stopPropagation();
            formDevolucion.classList.add('was-validated');
            return;
        }
        
        // Recopilar datos del formulario
        const pedidoId = selectPedido.value;
        const productosSeleccionados = Array.from(selectProductos.selectedOptions).map(option => {
            return {
                id: option.value,
                nombre: option.textContent
            };
        });
        
        if (productosSeleccionados.length === 0) {
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Debes seleccionar al menos un producto'
            });
            return;
        }
        
        // Crear objeto de devolución
        const devolucion = {
            id: generarId(),
            fecha: new Date(),
            estado: 'En proceso',
            pedidoId: pedidoId,
            productos: productosSeleccionados,
            motivo: document.getElementById('motivo').value,
            cantidad: document.getElementById('cantidad').value,
            descripcion: document.getElementById('descripcion').value,
            abierto: document.querySelector('input[name="abierto"]:checked').value,
            empaque: document.querySelector('input[name="empaque"]:checked').value,
            preferencia: document.getElementById('preferencia').value,
            direccion: document.getElementById('direccion').value,
            evidencia: document.getElementById('evidencia').files.length > 0 ? 
                Array.from(document.getElementById('evidencia').files).map(file => file.name).join(', ') : 
                'No se adjuntó evidencia'
        };
        
        // Guardar la devolución
        devoluciones.push(devolucion);
        ultimaDevolucionTiempo = new Date();
        
        // Persistir en localStorage
        guardarDevoluciones();
        
        // Actualizar UI
        actualizarListaDevoluciones();
        
        // Cerrar modal y mostrar mensaje de éxito
        modalDevolucion.hide();
        Swal.fire({
            icon: 'success',
            title: '¡Enviado!',
            text: 'Su solicitud de devolución se ha enviado correctamente. Te contactaremos pronto.'
        });
    }
    
    function cargarDevoluciones() {
        // Si hay devoluciones, mostrarlas
        if (devoluciones.length > 0) {
            listaVacia.classList.add('d-none');
            listaDevoluciones.classList.remove('d-none');
            actualizarListaDevoluciones();
        } else {
            listaVacia.classList.remove('d-none');
            listaDevoluciones.classList.add('d-none');
        }
    }
    
    function actualizarListaDevoluciones() {
        // Actualizar UI
        listaVacia.classList.add('d-none');
        listaDevoluciones.classList.remove('d-none');
        
        // Limpiar lista actual
        listaDevoluciones.innerHTML = '';
        
        // Mostrar cada devolución
        devoluciones.forEach((devolucion, index) => {
            const itemDevolucion = crearItemDevolucion(devolucion, index);
            listaDevoluciones.appendChild(itemDevolucion);
        });
        
        // Configurar botones de ver solicitud
        document.querySelectorAll('.btn-ver-solicitud').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = this.getAttribute('data-index');
                mostrarDetalleDevolucion(devoluciones[index]);
            });
        });
        
        // Configurar botones de eliminar
        document.querySelectorAll('.btn-eliminar').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = this.getAttribute('data-index');
                intentarEliminarDevolucion(index);
            });
        });
    }
    
    function crearItemDevolucion(devolucion, index) {
        const div = document.createElement('div');
        div.className = 'devolucion-item mb-3';
        
        const fechaFormateada = formatearFecha(devolucion.fecha);
        
        const claseEstado = devolucion.estado === 'En proceso' ? 'estado-proceso' : 'estado-completada';
        
        div.innerHTML = `
            <div class="d-flex justify-content-between align-items-center flex-wrap">
                <div>
                    <div class="d-flex align-items-center mb-2">
                        <span class="fw-bold me-3">Id: ${devolucion.id}</span>
                        <span class="text-muted">fecha: ${fechaFormateada}</span>
                    </div>
                    <div>
                        <span class="fw-bold">Estado: </span>
                        <span class="${claseEstado}">${devolucion.estado}</span>
                    </div>
                </div>
                <div class="devolucion-actions d-flex align-items-center">
                    <button class="btn btn-ver-solicitud me-2" data-index="${index}">Ver Solicitud</button>
                    <button class="btn-eliminar" data-index="${index}"><i class="fas fa-trash-alt"></i></button>
                </div>
            </div>
        `;
        
        return div;
    }
    
    function mostrarDetalleDevolucion(devolucion) {
        const detallesSolicitud = document.getElementById('detallesSolicitud');
        
        const productosTexto = devolucion.productos.map(p => p.nombre).join(', ');
        
        detallesSolicitud.innerHTML = `
            <div class="row mb-3">
                <div class="col-md-6">
                    <p><strong>ID de Solicitud:</strong> ${devolucion.id}</p>
                    <p><strong>Fecha:</strong> ${formatearFecha(devolucion.fecha)}</p>
                    <p><strong>Estado:</strong> <span class="${devolucion.estado === 'En proceso' ? 'estado-proceso' : 'estado-completada'}">${devolucion.estado}</span></p>
                    <p><strong>Pedido:</strong> #${devolucion.pedidoId}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Productos:</strong> ${productosTexto}</p>
                    <p><strong>Cantidad:</strong> ${devolucion.cantidad}</p>
                    <p><strong>Motivo:</strong> ${obtenerTextoMotivo(devolucion.motivo)}</p>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-12">
                    <p><strong>Descripción adicional:</strong></p>
                    <p>${devolucion.descripcion || 'No se proporcionó descripción adicional'}</p>
                </div>
            </div>
            <div class="row mb-3">
                <div class="col-md-6">
                    <p><strong>¿Producto abierto/usado?:</strong> ${devolucion.abierto === 'si' ? 'Sí' : 'No'}</p>
                    <p><strong>¿En empaque original?:</strong> ${devolucion.empaque === 'si' ? 'Sí' : 'No'}</p>
                </div>
                <div class="col-md-6">
                    <p><strong>Preferencia de resolución:</strong> ${devolucion.preferencia === 'reemplazo' ? 'Reemplazo del producto' : 'Reembolso'}</p>
                    <p><strong>Evidencia:</strong> ${devolucion.evidencia}</p>
                </div>
            </div>
            <div class="row">
                <div class="col-12">
                    <p><strong>Dirección de recogida/envío:</strong></p>
                    <p>${devolucion.direccion || 'No se proporcionó dirección'}</p>
                </div>
            </div>
        `;
        
        modalVerSolicitud.show();
    }
    
    function intentarEliminarDevolucion(index) {
        const devolucion = devoluciones[index];
        const ahora = new Date();
        const tiempoCreacion = new Date(devolucion.fecha);
        
        // Verificar si han pasado menos de 10 minutos
        const diferenciaMinutos = (ahora - tiempoCreacion) / (1000 * 60);
        
        if (diferenciaMinutos <= 10) {
            // Confirmar eliminación
            Swal.fire({
                title: '¿Estás seguro?',
                text: "¿Deseas eliminar esta solicitud de devolución?",
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, eliminar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    // Eliminar la devolución
                    devoluciones.splice(index, 1);
                    
                    // Persistir cambios en localStorage
                    guardarDevoluciones();
                    
                    actualizarListaDevoluciones();
                    
                    Swal.fire(
                        'Eliminada',
                        'La solicitud de devolución ha sido eliminada.',
                        'success'
                    );
                    
                    // Si no quedan devoluciones, mostrar mensaje vacío
                    if (devoluciones.length === 0) {
                        listaVacia.classList.remove('d-none');
                        listaDevoluciones.classList.add('d-none');
                    }
                }
            });
        } else {
            // Mostrar mensaje de que ya no se puede eliminar
            Swal.fire({
                icon: 'error',
                title: 'No se puede eliminar',
                text: 'Solo puedes eliminar solicitudes dentro de los primeros 10 minutos después de crearlas.'
            });
        }
    }
    
    function generarId() {
        // Generar ID único basado en timestamp y número aleatorio
        const timestamp = Date.now();
        const random = Math.floor(Math.random() * 1000);
        return parseInt(timestamp.toString().slice(-6) + random.toString().padStart(3, '0'));
    }
    
    function formatearFecha(fecha) {
        // Formatear fecha como DD-MM-YYYY
        const f = new Date(fecha);
        const dia = String(f.getDate()).padStart(2, '0');
        const mes = String(f.getMonth() + 1).padStart(2, '0');
        const año = f.getFullYear();
        
        return `${dia}-${mes}-${año}`;
    }
    
    function obtenerTextoMotivo(motivo) {
        const motivos = {
            'defectuoso': 'Producto defectuoso',
            'dañado': 'Producto dañado en tránsito',
            'equivocado': 'Producto equivocado',
            'incompleto': 'Pedido incompleto',
            'arrepentimiento': 'Ya no lo necesito',
            'otro': 'Otro motivo'
        };
        
        return motivos[motivo] || motivo;
    }
    
    // Función adicional para limpiar localStorage (útil para desarrollo/testing)
    function limpiarDevoluciones() {
        localStorage.removeItem('devoluciones');
        devoluciones = [];
        cargarDevoluciones();
    }
    
    // Exponer función de limpieza globalmente para uso en consola (opcional)
    window.limpiarDevoluciones = limpiarDevoluciones;
});