const carritoKey = 'carrito';

const guardarCarrito = carrito => localStorage.setItem(carritoKey, JSON.stringify(carrito));
const obtenerCarrito = () => JSON.parse(localStorage.getItem(carritoKey) || '[]');

const actualizarIconoCarrito = () => {
  const total = obtenerCarrito().reduce((acc, item) => acc + item.cantidad, 0);
  const icono = document.getElementById('cartCount');
  if (icono) icono.textContent = total;

  document.addEventListener('visibilitychange', () => {
  if (document.visibilityState === 'visible') {
    actualizarIconoCarrito();
  }
  });
  
};

const agregarAlCarrito = (idProducto, nombre, precio, cantidad, imagen) => {
  console.log("agregarAlCarrito llamado con:", idProducto, nombre, precio, cantidad, imagen);
  const carrito = obtenerCarrito();
  const prod = carrito.find(p => p.idProducto === idProducto);
  if (prod) prod.cantidad += cantidad;
  else carrito.push({ idProducto, nombre, precio, cantidad, imagen, agregadoEn: Date.now() });
  guardarCarrito(carrito);
  actualizarIconoCarrito();
  console.log('Producto agregado:', carrito);

const alerta = document.getElementById('alerta-carrito');
if (alerta) {
  alerta.classList.remove('d-none');
  alerta.classList.add('show');

  setTimeout(() => {
    alerta.classList.remove('show');
    alerta.classList.add('d-none');
  }, 1000);
}

};

function getStarsHTML(rating) {
    let starsHTML = '';
    for (let i = 1; i <= 5; i++) {
        starsHTML += `<span class="star ${i <= rating ? 'active' : ''}" data-value="${i}">&#9733;</span>`;
    }
    return starsHTML;
}

function enviarCalificacion(id_producto, calificacion) {
    fetch('/guardar-calificacion/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `id_producto=${id_producto}&calificacion=${calificacion}`
    })
    .then(response => response.json())
    .then(data => {
        const msg = document.getElementById("mensaje-calificacion");
        msg.textContent = data.mensaje;
        msg.classList.remove("d-none");
        setTimeout(() => msg.classList.add("d-none"), 2000);

        if (data.success) {
            const ratingText = document.querySelector('.rating-text');
            if (ratingText) ratingText.textContent = `(${data.nuevo_promedio})`;

            const reviewSpan = document.getElementById(`review-count-${id_producto}`);
            if (reviewSpan) reviewSpan.textContent = `(${data.total_reviews})`;
        } else {
            console.error('Error al guardar la calificación:', data.mensaje);
        }
    });
}

function showProductDetails(card) {
    const idProducto = card.getAttribute('data-id');
    const nombre = card.getAttribute('data-nombre');
    const precio = parseFloat(card.getAttribute('data-precio')).toLocaleString();
    const imagen = card.getAttribute('data-imagen');
    const descripcion = card.getAttribute('data-descripcion');
    const cantidad = card.getAttribute('data-cantidad');
    const rating = parseFloat(card.getAttribute('data-rating')) || 4;

    const ratingStars = getStarsHTML(rating);

    document.getElementById("productDetails").innerHTML = `
        <div class="image-container mb-3 text-center">
            <img src="${imagen}" alt="${nombre}" class="img-fluid" style="max-height: 300px; object-fit: contain;">
        </div>
        <div class="product-details">
            <h3 class="product-title">${nombre}</h3>
            <div class="d-flex align-items-center mb-2">
                <div class="stars">${ratingStars}</div>
                <span class="ms-2 rating-text">(${rating.toFixed(1)})</span>
            </div>
            <h4 class="price">$${precio}</h4>
            <p>${descripcion}</p>
            <p class="text-success">Envío gratis a todo el país</p>
            <div class="d-flex align-items-center mb-3">
                <button class="btn btn-outline-secondary" id="decreaseQuantity">-</button>
                <input type="number" id="productQuantity" value="1" min="1" class="mx-2" style="width: 60px; text-align: center;">
                <button class="btn btn-outline-secondary" id="increaseQuantity">+</button>
            </div>
            <p>Cantidad disponible: <span id="stockQuantity">${cantidad}</span></p>
        </div>
    `;

    const modal = document.getElementById('productModal');
    modal.setAttribute('data-id-producto', idProducto);
    modal.setAttribute('data-imagen-producto', imagen);  // Guardamos la imagen aquí también

    const increaseBtn = document.getElementById("increaseQuantity");
    const decreaseBtn = document.getElementById("decreaseQuantity");
    const quantityInput = document.getElementById("productQuantity");

    increaseBtn.addEventListener("click", () => {
        quantityInput.value = parseInt(quantityInput.value) + 1;
    });

    decreaseBtn.addEventListener("click", () => {
        if (quantityInput.value > 1) {
            quantityInput.value = parseInt(quantityInput.value) - 1;
        }
    });

    const stars = document.querySelectorAll('.stars .star');
    stars.forEach(star => {
        star.addEventListener('click', () => {
            const selectedRating = star.getAttribute('data-value');
            stars.forEach(s => s.classList.toggle('active', s.getAttribute('data-value') <= selectedRating));
            enviarCalificacion(idProducto, selectedRating);
        });
    });
}

document.addEventListener('DOMContentLoaded', () => {
  actualizarIconoCarrito();

  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('click', (e) => {
      const clickedInsideButton = e.target.classList.contains('add-to-cart-btn') || e.target.closest('.add-to-cart-btn');
      if (clickedInsideButton) {
        e.stopPropagation();
        agregarAlCarrito(
          card.getAttribute('data-id'),
          card.getAttribute('data-nombre'),
          parseFloat(card.getAttribute('data-precio')),
          1,
          card.getAttribute('data-imagen')  // Aquí pasamos la imagen
        );
        return;
      }
      showProductDetails(card);
      const modal = new bootstrap.Modal(document.getElementById('productModal'));
      modal.show();
    });
  });

  const addToCartModalBtn = document.getElementById('add-to-cart-modal');
  addToCartModalBtn.onclick = () => {
    console.log("Botón modal clickeado");
    const modal = document.getElementById('productModal');
    const cantidad = parseInt(document.getElementById('productQuantity').value);
    const nombre = document.querySelector('#productDetails .product-title').textContent;
    const precio = parseFloat(document.querySelector('#productDetails .price').textContent.replace(/[^0-9.-]+/g,""));
    const idProducto = modal.getAttribute('data-id-producto');
    const imagen = modal.getAttribute('data-imagen-producto');  // Obtenemos imagen del atributo

    if (!idProducto) return console.error('No se encontró el id del producto en el modal');
    agregarAlCarrito(idProducto, nombre, precio, cantidad, imagen);
  };

  const searchInput = document.getElementById('query');
  searchInput.addEventListener('input', () => {
    const filtro = searchInput.value.toLowerCase().trim();
    const cards = document.querySelectorAll('#productList .card');

    cards.forEach(card => {
      const nombre = card.getAttribute('data-nombre').toLowerCase();
      if (nombre.includes(filtro)) {
        card.parentElement.style.display = '';
      } else {
        card.parentElement.style.display = 'none';
      }
    });
  });
});