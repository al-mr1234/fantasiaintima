// Recuperar carrito del localStorage o inicializar vacío
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Mostrar productos en el carrito
function showCart() {
    const cartContainer = document.getElementById('cart-container');
    const totalAmount = document.getElementById('total-amount');
    cartContainer.innerHTML = '';
    let subtotal = 0;

    if (cart.length === 0) {
        cartContainer.innerHTML = "<p>No hay productos en el carrito.</p>";
        totalAmount.textContent = "$0";
        return;
    }

    cart.forEach((product, index) => {
        const productTotal = product.price * product.quantity;
        subtotal += productTotal;

        const formattedPrice = product.price.toLocaleString('es-CO');
        const formattedSubtotal = productTotal.toLocaleString('es-CO');

        const cartItem = `
            <div class="cart-item">
                <img src="${product.image}" alt="${product.name}" class="product-image">
                <div class="product-details">
                    <h5>${product.name}</h5>
                    <p>${product.details}</p>
                    <h3 class="price">Precio: $${formattedPrice}</h3>
                </div>
                <div class="product-actions">
                    <p class="subtotal">Subtotal: $${formattedSubtotal}</p>
                    <div class="quantity">
                        <button class="btn-quantity" onclick="decrementQuantity(${index})">-</button>
                        <input type="number" id="cantidad-${index}" min="1" value="${product.quantity}" 
                               onchange="updateQuantity(${index}, this.value)">
                        <button class="btn-quantity" onclick="incrementQuantity(${index})">+</button>
                    </div>
                    <button class="btn-icon" onclick="removeFromCart(${index})" title="Eliminar">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
        `;
        cartContainer.innerHTML += cartItem;
    });

    totalAmount.textContent = `$${subtotal.toLocaleString('es-CO')}`;
}

// Incrementar cantidad
function incrementQuantity(index) {
    cart[index].quantity += 1;
    localStorage.setItem('cart', JSON.stringify(cart));
    showCart();
}

// Decrementar cantidad
function decrementQuantity(index) {
    if (cart[index].quantity > 1) {
        cart[index].quantity -= 1;
        localStorage.setItem('cart', JSON.stringify(cart));
        showCart();
    } else {
        removeFromCart(index);
    }
}

// Actualizar cantidad de un producto
function updateQuantity(index, quantity) {
    if (quantity < 1) {
        removeFromCart(index);
        return;
    }
    cart[index].quantity = parseInt(quantity);
    localStorage.setItem('cart', JSON.stringify(cart));
    showCart();
}

// Eliminar un producto del carrito
function removeFromCart(index) {
    cart.splice(index, 1);
    localStorage.setItem('cart', JSON.stringify(cart));
    showCart();
}

// Vaciar el carrito
function clearCart() {
    cart = [];
    localStorage.setItem('cart', JSON.stringify(cart));
    showCart();
}

// Proceder al pago
function checkout() {
    if (cart.length === 0) {
        alert("Tu carrito está vacío.");
        return;
    }
    alert("Redirigiendo a la página de pago...");
}

// Función para volver atrás
function goBack() {
    window.history.back(); // Volver a la página anterior
}

// Inicializar la vista del carrito
document.addEventListener("DOMContentLoaded", showCart);

//alerta de formulario de entrega
document.getElementById("formPago").addEventListener("submit", function (e) {
    e.preventDefault();

    Swal.fire({
      icon: 'success',
      title: '¡Datos entregados!',
      text: 'Tu información para la entrega de los productos ha sido enviada.',
      confirmButtonColor: '#f5365c',
      confirmButtonText: 'Aceptar',
      customClass: {
        popup: 'rounded-4'
      }
    }).then((result) => {
      if (result.isConfirmed) {
        // Cerrar el modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('paymentModal'));
        modal.hide();

        // Limpiar el formulario
        document.getElementById("formPago").reset();

        // Vaciar el carrito
        clearCart();
      }
    });
  });

