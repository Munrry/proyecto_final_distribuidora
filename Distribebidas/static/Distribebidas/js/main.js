console.log("Distribebidas JS cargado ✨");

// ========================================
// SUBTOTAL DINÁMICO EN TABLAS
// ========================================
function calcularFilaSubtotal(row) {
  const cantidad = parseFloat(row.querySelector('.cantidad')?.value || 0);
  const precio = parseFloat(row.querySelector('.precio')?.value || 0);
  const subtotal = (cantidad * precio).toFixed(2);

  const celda = row.querySelector('.subtotal');
  if (celda) celda.textContent = subtotal;
}

document.addEventListener("input", function (e) {
  if (e.target.matches(".cantidad") || e.target.matches(".precio")) {
    const row = e.target.closest("tr");
    if (row) calcularFilaSubtotal(row);
  }
});

// Listener para cambiar el stock dinámicamente según la presentación elegida
document.addEventListener("DOMContentLoaded", function () {
    const selectPresentacion = document.getElementById("presentacion-select");
    const stockDisplay = document.getElementById("stock-dinamico");
    const btnAgregar = document.querySelector(".btn-agregar-carrito"); // Ajusta la clase según tu botón

    if (selectPresentacion && stockDisplay) {
        selectPresentacion.addEventListener("change", function () {
            // Obtenemos la opción seleccionada por el usuario
            const opcionSeleccionada = this.options[this.selectedIndex];
            
            // Extraemos el stock del atributo de la opción
            const nuevoStock = parseInt(opcionSeleccionada.getAttribute("data-stock")) || 0;
            
            // Actualizamos el número en el HTML
            stockDisplay.textContent = nuevoStock;

            // Bloqueamos o desbloqueamos el botón según el stock del tamaño elegido
            if (btnAgregar) {
                if (nuevoStock <= 0) {
                    btnAgregar.disabled = true;
                    btnAgregar.innerHTML = '<i class="bi bi-x-circle"></i> Agotado';
                } else {
                    btnAgregar.disabled = false;
                    btnAgregar.innerHTML = '<i class="bi bi-cart-plus"></i> Agregar al carrito';
                }
            }
        });
    }
});

// ========================================
// ANIMACIONES AL CARGAR PÁGINA
// ========================================
document.addEventListener("DOMContentLoaded", function () {
  
  // Animación de eliminación de productos del carrito
  document.querySelectorAll(".eliminar-form").forEach(form => {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      const row = form.closest("tr");
      row.classList.add("tr-eliminado");
      setTimeout(() => {
        form.submit();
      }, 500);
    });
  });

  // Animación de iconos del navbar
  document.querySelectorAll(".nav-anim-icon").forEach(icon => {
    icon.addEventListener("click", function () {
      icon.classList.add("nav-icon-clicked");
      setTimeout(() => icon.classList.remove("nav-icon-clicked"), 300);
    });
  });

  // Animación de botones
  document.querySelectorAll(".btn").forEach(btn => {
    btn.addEventListener("click", function () {
      btn.classList.add("btn-clicked");
      setTimeout(() => btn.classList.remove("btn-clicked"), 300);
    });
  });

  // ========================================
  // VALIDACIÓN DE CONTRASEÑA EN TIEMPO REAL
  // ========================================
  const passwordForm = document.getElementById("passwordForm");
  if (passwordForm) {
    const old = passwordForm.querySelector('input[name="old_password"]');
    const new1 = passwordForm.querySelector('input[name="new_password1"]');
    const new2 = passwordForm.querySelector('input[name="new_password2"]');
    const btnCambiar = document.getElementById("btnCambiar");
    const msg = document.getElementById("passwordMsg");

    function validarPassword() {
      if (new1 && new2 && msg) {
        let error = "";
        
        if (new1.value.length > 0 && new1.value.length < 8) {
          error = "La contraseña debe tener al menos 8 caracteres.";
        } else if (new2.value.length > 0 && new1.value !== new2.value) {
          error = "Las contraseñas no coinciden.";
        } else if (new1.value === new2.value && new1.value.length >= 8) {
          error = "";
        }

        if (error) {
          msg.textContent = error;
          msg.classList.add("show");
          btnCambiar.disabled = true;
        } else {
          msg.textContent = "";
          msg.classList.remove("show");
          btnCambiar.disabled = false;
        }
      }
    }

    if (new1) new1.addEventListener("input", validarPassword);
    if (new2) new2.addEventListener("input", validarPassword);
    validarPassword();
  }

  // ========================================
  // ANIMACIÓN DE INPUTS EN FORMULARIOS
  // ========================================
  document.querySelectorAll('.auth-input-group input').forEach(input => {
    input.addEventListener('focus', function() {
      this.parentElement.classList.add('focused');
    });
    
    input.addEventListener('blur', function() {
      if (!this.value) {
        this.parentElement.classList.remove('focused');
      }
    });
  });

  // ========================================
  // VISTA PREVIA DE FACTURA PDF
  // ========================================
  const pdfPreviewBtn = document.getElementById("previewPdfBtn");
  if (pdfPreviewBtn) {
    pdfPreviewBtn.addEventListener("click", function(e) {
      e.preventDefault();
      const facturaId = this.getAttribute("data-factura-id");
      mostrarVistaPrevia(facturaId);
    });
  }

  const closePdfModal = document.getElementById("closePdfModal");
  if (closePdfModal) {
    closePdfModal.addEventListener("click", function() {
      document.getElementById("pdfPreviewModal").classList.remove("show");
    });
  }

  // Cerrar modal al hacer clic fuera
  const pdfModal = document.getElementById("pdfPreviewModal");
  if (pdfModal) {
    pdfModal.addEventListener("click", function(e) {
      if (e.target === pdfModal) {
        pdfModal.classList.remove("show");
      }
    });
  }

  // ========================================
  // VALIDACIÓN EN TIEMPO REAL - REGISTRO
  // ========================================
  const registroForm = document.querySelector('form[action*="registro"]');
  if (registroForm) {
    const email = registroForm.querySelector('input[name="email"]');
    const password1 = registroForm.querySelector('input[name="password1"]');
    const password2 = registroForm.querySelector('input[name="password2"]');
    
    if (password1 && password2) {
      password2.addEventListener('input', function() {
        if (password2.value && password1.value !== password2.value) {
          password2.setCustomValidity("Las contraseñas no coinciden");
        } else {
          password2.setCustomValidity("");
        }
      });
    }
  }

  // ========================================
  // EFECTOS VISUALES MEJORADOS
  // ========================================
  
  // Efecto parallax suave en cards
  document.querySelectorAll('.card').forEach(card => {
    card.addEventListener('mousemove', function(e) {
      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      const centerX = rect.width / 2;
      const centerY = rect.height / 2;
      
      const rotateX = (y - centerY) / 20;
      const rotateY = (centerX - x) / 20;
      
      card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
    });
    
    card.addEventListener('mouseleave', function() {
      card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) scale(1)';
    });
  });

  // Animación de carga para elementos
  const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
  };

  const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.animation = 'fadeInUp 0.6s ease-out forwards';
        observer.unobserve(entry.target);
      }
    });
  }, observerOptions);

  document.querySelectorAll('.card, .table, .perfil-card').forEach(el => {
    el.style.opacity = '0';
    observer.observe(el);
  });
});

// ========================================
// FUNCIÓN PARA VISTA PREVIA DE FACTURA
// ========================================
function mostrarVistaPrevia(facturaId) {
  const modal = document.getElementById("pdfPreviewModal");
  const content = document.getElementById("pdfPreviewModalContent");
  
  if (!modal || !content) return;
  
  // Mostrar loading
  content.innerHTML = '<div class="text-center"><div class="spinner-border text-warning" role="status"></div><p class="mt-3">Cargando vista previa...</p></div>';
  modal.classList.add("show");
  
  // Obtener contenido de la factura
  fetch(`/factura/${facturaId}/`)
    .then(response => response.text())
    .then(html => {
      // Extraer solo el contenido de la factura
      const parser = new DOMParser();
      const doc = parser.parseFromString(html, 'text/html');
      const facturaContent = doc.querySelector('.container');
      
      if (facturaContent) {
        content.innerHTML = facturaContent.innerHTML;
      } else {
        content.innerHTML = '<p class="text-danger">Error al cargar la vista previa</p>';
      }
    })
    .catch(error => {
      console.error('Error:', error);
      content.innerHTML = '<p class="text-danger">Error al cargar la vista previa</p>';
    });
}

// ========================================
// EFECTOS DE PARTÍCULAS (OPCIONAL)
// ========================================
function createParticle(x, y) {
  const particle = document.createElement('div');
  particle.style.position = 'fixed';
  particle.style.left = x + 'px';
  particle.style.top = y + 'px';
  particle.style.width = '4px';
  particle.style.height = '4px';
  particle.style.background = '#ffd966';
  particle.style.borderRadius = '50%';
  particle.style.pointerEvents = 'none';
  particle.style.zIndex = '9999';
  particle.style.opacity = '1';
  document.body.appendChild(particle);
  
  const angle = Math.random() * Math.PI * 2;
  const velocity = 2 + Math.random() * 3;
  const vx = Math.cos(angle) * velocity;
  const vy = Math.sin(angle) * velocity;
  
  let opacity = 1;
  let posX = x;
  let posY = y;
  
  function animate() {
    posX += vx;
    posY += vy;
    opacity -= 0.02;
    
    particle.style.left = posX + 'px';
    particle.style.top = posY + 'px';
    particle.style.opacity = opacity;
    
    if (opacity > 0) {
      requestAnimationFrame(animate);
    } else {
      particle.remove();
    }
  }
  
  animate();
}

// Agregar partículas al hacer clic en botones importantes
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.auth-btn, .btn-dark').forEach(btn => {
    btn.addEventListener('click', function(e) {
      for (let i = 0; i < 8; i++) {
        setTimeout(() => {
          createParticle(e.clientX, e.clientY);
        }, i * 20);
      }
    });
  });
});

document.addEventListener('DOMContentLoaded', function() {
  const previewBtn = document.getElementById('previewPdfBtn');
  const modal = document.getElementById('pdfPreviewModal');
  const closeBtn = document.getElementById('closePdfModal');
  const modalContent = document.getElementById('pdfPreviewModalContent');
  
  if (previewBtn) {
    previewBtn.addEventListener('click', function() {
      // Clonar el contenido de la factura
      const facturaContent = document.querySelector('.perfil-card').cloneNode(true);
      
      // Remover los botones del contenido clonado
      const buttons = facturaContent.querySelectorAll('.d-flex.gap-2');
      buttons.forEach(btn => btn.remove());
      
      modalContent.innerHTML = '';
      modalContent.appendChild(facturaContent);
      
      modal.classList.add('show');
    });
  }
  
  if (closeBtn) {
    closeBtn.addEventListener('click', function() {
      modal.classList.remove('show');
    });
  }
  
  if (modal) {
    modal.addEventListener('click', function(e) {
      if (e.target === modal) {
        modal.classList.remove('show');
      }
    });
  }
});
document.addEventListener('DOMContentLoaded', function() {
  const inputs = document.querySelectorAll('.auth-input-group input');
  
  inputs.forEach(input => {
    input.addEventListener('blur', function() {
      if (this.value.trim() === '') {
        this.style.borderColor = 'var(--accent-red)';
        this.style.boxShadow = '0 0 12px rgba(255, 82, 82, 0.3)';
      } else {
        this.style.borderColor = 'var(--accent-green)';
        this.style.boxShadow = '0 0 12px rgba(76, 175, 80, 0.3)';
      }
    });
    
    input.addEventListener('input', function() {
      if (this.checkValidity()) {
        this.style.borderColor = 'var(--accent-green)';
      } else {
        this.style.borderColor = 'var(--accent-red)';
      }
    });
  });
  
  // Validación de email
  const emailInput = document.querySelector('input[type="email"]');
  if (emailInput) {
    emailInput.addEventListener('blur', function() {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(this.value)) {
        this.style.borderColor = 'var(--accent-red)';
        this.setCustomValidity('Email inválido');
      } else {
        this.style.borderColor = 'var(--accent-green)';
        this.setCustomValidity('');
      }
    });
  }
});