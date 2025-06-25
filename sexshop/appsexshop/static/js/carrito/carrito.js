document.addEventListener('DOMContentLoaded', () => {
  mostrarCarrito();

  document.getElementById('formPago').addEventListener('submit', function (e) {
    e.preventDefault();
    registrarPago();
  });
});

function mostrarCarrito() {
  const cartContainer = document.getElementById('cart-container');
  const totalAmount = document.getElementById('total-amount');
  const carrito = JSON.parse(localStorage.getItem('carrito')) || [];

  cartContainer.innerHTML = '';
  let total = 0;

  if (carrito.length === 0) {
    cartContainer.innerHTML = '<p class="text-center">Tu carrito está vacío.</p>';
    totalAmount.textContent = '$0.00';
    return;
  }

  carrito.sort((a, b) => b.IdProducto - a.IdProducto);

  carrito.forEach((producto, index) => {
    // Deshabilitar "+" si cantidad == stock
    const plusDisabled = producto.cantidad >= producto.stock ? 'disabled' : '';
    const minusDisabled = producto.cantidad <= 1 ? 'disabled' : '';
    const item = document.createElement('div');
    item.className = 'card mb-3';
    item.innerHTML = `
      <div class="card-body d-flex justify-content-between align-items-center">
        <div class="d-flex align-items-center gap-3" style="max-width: 60%;">
          <img src="${producto.imagen}" alt="${producto.nombre}" style="width: 100px; height: 120px; object-fit: cover; border-radius: 10px;">
          <div>
            <h5 class="card-title mb-1">${producto.nombre}</h5>
            <p class="card-text mb-1">${producto.descripcion || ''}</p>
            <p class="card-text mb-1">Precio unitario: $${producto.precio.toLocaleString('es-CL')}</p>
          </div>
        </div>
        <div class="text-end" style="min-width: 160px;">
          <p class="mb-2 fw-bold">$${(producto.precio * producto.cantidad).toLocaleString('es-CL')}</p>
          <div class="d-flex flex-column align-items-end gap-2">
            <div class="d-flex align-items-center gap-2 mb-2">
              <button class="btn btn-sm btn-outline-secondary" onclick="cambiarCantidad('${producto.IdProducto}', -1)" ${minusDisabled}>-</button>
              <span>${producto.cantidad}</span>
              <button class="btn btn-sm btn-outline-secondary" onclick="cambiarCantidad('${producto.IdProducto}', 1)" ${plusDisabled}>+</button>
            </div>
            <button class="btn btn-sm btn-danger" onclick="eliminarDelCarrito('${producto.IdProducto}')">
              <i class="fas fa-trash-alt"></i>
            </button>
          </div>
        </div>
      </div>
    `;
    cartContainer.appendChild(item);
    total += producto.precio * producto.cantidad;
  });

  totalAmount.textContent = `$${total.toLocaleString('es-CL')}`;
}

// Cambia la función para eliminar por IdProducto
function eliminarDelCarrito(idProducto) {
  let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
  carrito = carrito.filter(p => p.IdProducto != idProducto);
  localStorage.setItem('carrito', JSON.stringify(carrito));
  mostrarCarrito();
}

function cambiarCantidad(idProducto, cambio) {
  let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
  const prod = carrito.find(p => p.IdProducto == idProducto);
  if (prod) {
    // Limitar la cantidad máxima al stock disponible
    const maxStock = prod.stock !== undefined ? prod.stock : 99;
    let nuevaCantidad = prod.cantidad + cambio;
    if (nuevaCantidad < 1) nuevaCantidad = 1;
    if (nuevaCantidad > maxStock) nuevaCantidad = maxStock;
    prod.cantidad = nuevaCantidad;
    localStorage.setItem('carrito', JSON.stringify(carrito));
    mostrarCarrito();
  }
}

function clearCart() {
  Swal.fire({
    title: '¿Estás seguro?',
    text: 'Esto vaciará todo tu carrito.',
    icon: 'warning',
    showCancelButton: true,
    confirmButtonColor: '#f5365c',
    cancelButtonColor: '#6c757d',
    confirmButtonText: 'Sí, vaciar',
  }).then((result) => {
    if (result.isConfirmed) {
      localStorage.removeItem('carrito');
      mostrarCarrito();
      Swal.fire('Carrito vaciado', '', 'success');
    }
  });
}

function registrarPago() {
  const nombre = document.getElementById('nombreCompleto').value;
  const direccion = document.getElementById('direccion').value;
  const correo = document.getElementById('correo').value;
  const telefono = document.getElementById('telefono').value;
  const fechaEntrega = document.getElementById('fechaEntrega').value;
  const carrito = JSON.parse(localStorage.getItem('carrito')) || [];

  if (carrito.length === 0) {
    Swal.fire('Carrito vacío', 'Agrega productos antes de pagar.', 'info');
    return;
  }

  const datos = {
    nombre, direccion, correo, telefono, fechaEntrega, carrito
  };

  fetch('/registrar-pago/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify(datos),
  })
    .then(response => {
      if (response.ok) {
        Swal.fire('¡Pago registrado!', 'Gracias por tu compra.', 'success');
        localStorage.removeItem('carrito');
        mostrarCarrito();
        document.getElementById('formPago').reset();
        const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
        modal.hide();
      } else {
        throw new Error('Error al registrar el pago');
      }
    })
    .catch(() => {
      Swal.fire('Error', 'No se pudo registrar el pago. Intenta de nuevo.', 'error');
    });
}

function goBack() {
  window.history.back();
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let c of cookies) {
      const cookie = c.trim();
      if (cookie.startsWith(name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
