document.addEventListener('DOMContentLoaded', () => {
  // Al cargar la página, sincroniza el carrito local con el backend si el usuario está logueado
  const userDataElement = document.getElementById('user-data');
  if (userDataElement && userDataElement.dataset.username) {
    cargarCarritoDesdeBackend();
  } else {
    mostrarCarrito();
  }

  // Event listener para el formulario de pago (si lo tienes en el modal)
  const formPago = document.getElementById('formPago');
  if (formPago) {
    formPago.addEventListener('submit', function (e) {
      e.preventDefault();
      registrarPago();
    });
  }
  // Event listener para el botón de PayPal
  const btnPayPal = document.getElementById('btnPayPal');
  if (btnPayPal) {
    btnPayPal.addEventListener('click', function () {
      // Solo muestra la alerta si el usuario NO está logueado
      if (!verificarSesion()) {
        return; // Detiene la ejecución si el usuario no está logueado
      }
      cargarCarritoDesdeBackend(); // sincroniza antes de pagar
      procesarPagoPayPal();
    });
  }
});

/**
 * Carga el carrito del usuario desde el backend y lo guarda en localStorage.
 * Llamar después de login y después de modificar el carrito.
 */
async function cargarCarritoDesdeBackend() {
  try {
    const response = await fetch('/api/obtener-carrito-usuario/');
    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('carrito', JSON.stringify(data.carrito));
      mostrarCarrito();
    } else {
      mostrarCarrito(); // fallback si falla
    }
  } catch (error) {
    mostrarCarrito(); // fallback si falla
  }
}

/**
 * Agrega un producto al carrito del usuario en el backend.
 * Llamar cuando el usuario agregue un producto al carrito.
 */
async function agregarProductoAlCarritoBackend(idProducto, cantidad = 1) {
  try {
    await fetch('/api/agregar-producto-carrito/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ id_producto: idProducto, cantidad }),
    });
    cargarCarritoDesdeBackend();
  } catch (error) {
    Swal.fire('Error', 'No se pudo agregar el producto al carrito.', 'error');
  }
}

// Ejemplo de función para usar en botones de productos
function agregarAlCarrito(idProducto, cantidad = 1) {
  if (!verificarSesion()) return;
  agregarProductoAlCarritoBackend(idProducto, cantidad);
}

/**
 * Verifica si el usuario ha iniciado sesión.
 * Solo muestra la alerta si NO está logueado y se intenta comprar.
 * @returns {boolean} true si el usuario está logueado, false en caso contrario.
 */
function verificarSesion() {
   const username = document.getElementById("user-info").dataset.username;
    console.log("Hola", username);
 
  if (username) return true;
  Swal.fire({
    title: 'Debes iniciar sesión',
    text: 'Por favor, inicia sesión para continuar con la compra.',
    icon: 'warning',
    confirmButtonColor: '#f5365c',
    confirmButtonText: 'Iniciar Sesión'
  }).then((result) => {
    if (result.isConfirmed) {
      window.location.href = '/login/';
    }
  });
  return false;
} 

function procesarPagoPayPal() {
  const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
  if (carrito.length === 0) {
    Swal.fire('Carrito vacío', 'Agrega productos antes de pagar.', 'info');
    return;
  }
  let total = 0;
  carrito.forEach(producto => {
    total += producto.precio * producto.cantidad;
  });
  fetch('/pago-paypal-carrito/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCookie('csrftoken'),
    },
    body: JSON.stringify({ total, carrito }),
  })
    .then(response => {
      if (!response.ok) {
        return response.json().then(err => { throw new Error(err.error || 'Error desconocido del servidor'); });
      }
      return response.json();
    })
    .then(data => {
      if (data.form_html) {
        const paypalFormContainer = document.getElementById('paypal-form-container');
        if (paypalFormContainer) {
          paypalFormContainer.innerHTML = data.form_html;
          const form = paypalFormContainer.querySelector('form');
          if (form) {
            form.submit();
          } else {
            Swal.fire('Error', 'No se encontró el formulario de PayPal en la respuesta.', 'error');
          }
        } else {
          Swal.fire('Error', 'Contenedor de formulario de PayPal no encontrado.', 'error');
        }
      } else {
        Swal.fire('Error', data.error || 'No se pudo generar el formulario de PayPal.', 'error');
      }
    })
    .catch(error => {
      console.error('Error en la solicitud de PayPal:', error);
      Swal.fire('Error', error.message || 'No se pudo conectar con el servidor o hubo un problema en la solicitud.', 'error');
    });
}

function mostrarCarrito() {
  const cartContainer = document.getElementById('cart-container');
  const totalAmount = document.getElementById('total-amount');
  const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
  if (!cartContainer || !totalAmount) {
    console.warn("Elementos 'cart-container' o 'total-amount' no encontrados. No se puede mostrar el carrito.");
    return;
  }
  cartContainer.innerHTML = '';
  let total = 0;
  if (carrito.length === 0) {
    cartContainer.innerHTML = '<p class="text-center">Tu carrito está vacío.</p>';
    totalAmount.textContent = '$0.00';
    return;
  }
  carrito.sort((a, b) => b.IdProducto - a.IdProducto);
  carrito.forEach((producto) => {
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

function eliminarDelCarrito(idProducto) {
  let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
  carrito = carrito.filter(p => p.IdProducto != idProducto);
  localStorage.setItem('carrito', JSON.stringify(carrito));
  mostrarCarrito();
  
  // Si está logueado, sincronizar con backend
  sincronizarCarritoConBackend();
}

function cambiarCantidad(idProducto, cambio) {
  let carrito = JSON.parse(localStorage.getItem('carrito')) || [];
  const prod = carrito.find(p => p.IdProducto == idProducto);
  if (prod) {
    const maxStock = prod.stock !== undefined ? prod.stock : 99;
    let nuevaCantidad = prod.cantidad + cambio;
    if (nuevaCantidad < 1) nuevaCantidad = 1;
    if (nuevaCantidad > maxStock) nuevaCantidad = maxStock;
    prod.cantidad = nuevaCantidad;
    localStorage.setItem('carrito', JSON.stringify(carrito));
    mostrarCarrito();
    
    // Si está logueado, sincronizar con backend
    sincronizarCarritoConBackend();
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
    cancelButtonText: 'No, cancelar'
  }).then((result) => {
    if (result.isConfirmed) {
      localStorage.removeItem('carrito');
      mostrarCarrito();
      Swal.fire('Carrito vaciado', '', 'success');
    }
  });
}

function registrarPago() {
  if (!verificarSesion()) {
    return;
  }
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
  if (!nombre || !direccion || !correo || !telefono || !fechaEntrega) {
    Swal.fire('Campos incompletos', 'Por favor, rellena todos los campos del formulario de pago.', 'warning');
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
        const formPago = document.getElementById('formPago');
        if (formPago) formPago.reset();
        const paymentModal = document.getElementById('paymentModal');
        if (paymentModal) {
          const modal = bootstrap.Modal.getInstance(paymentModal);
          if (modal) modal.hide();
        }
      } else {
        return response.json().then(err => { throw new Error(err.error || 'Error al registrar el pago'); });
      }
    })
    .catch((error) => {
      console.error('Error al registrar el pago:', error);
      Swal.fire('Error', error.message || 'No se pudo registrar el pago. Intenta de nuevo.', 'error');
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
document.addEventListener('DOMContentLoaded', () => {
  const userDataElement = document.getElementById('user-data');
  const isLoggedIn = userDataElement && userDataElement.dataset.username;
  
  if (isLoggedIn) {
    // Usuario logueado: cargar desde backend
    cargarCarritoDesdeBackend();
  } else {
    // Usuario invitado: usar localStorage
    mostrarCarrito();
  }

  // Resto del código...
});

/**
 * Carga el carrito del usuario desde el backend y reemplaza el localStorage
 */
async function cargarCarritoDesdeBackend() {
  try {
    const response = await fetch('/api/obtener-carrito-usuario/');
    if (response.ok) {
      const data = await response.json();
      // Reemplazar el carrito local con el del backend
      localStorage.setItem('carrito', JSON.stringify(data.carrito));
      mostrarCarrito();
    } else {
      // Si falla, mostrar carrito local como fallback
      mostrarCarrito();
    }
  } catch (error) {
    mostrarCarrito(); // fallback si falla
  }
}

/**
 * Sincroniza el carrito local con el backend (para usuarios logueados)
 */
async function sincronizarCarritoConBackend() {
  const userDataElement = document.getElementById('user-data');
  const isLoggedIn = userDataElement && userDataElement.dataset.username;
  
  if (!isLoggedIn) return; // Solo para usuarios logueados
  
  try {
    const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    const response = await fetch('/api/sincronizar-carrito/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken'),
      },
      body: JSON.stringify({ carrito }),
    });
    
    if (response.ok) {
      // Después de sincronizar, cargar la versión actualizada del backend
      await cargarCarritoDesdeBackend();
    }
  } catch (error) {
    console.error('Error sincronizando carrito:', error);
  }
}

function onLoginSuccess() {
  // Sincronizar el carrito local con el backend
  sincronizarCarritoConBackend();
}

// Cuando el usuario se desloguea
function onLogout() {
  // Limpiar el carrito local o mantenerlo para invitado
  // localStorage.removeItem('carrito'); // Opcional: limpiar al logout
  mostrarCarrito();
}

// --- Importante: Cómo pasar los datos de sesión de Django a JavaScript ---
// En tu plantilla HTML (ej. carrito.html), deberías tener algo como esto:
/*
<div id="user-data"
     data-username="{{ user.username }}"
     style="display: none;">
</div>
*/
// Esto permite que JavaScript acceda a los datos de sesión de forma segura.
// La función verificarSesion() ahora lee