
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-count]").forEach(counter => {
    const target = +counter.dataset.count;
    let value = 0;
    const increment = Math.ceil(target / 40); 

    const update = () => {
      if (value < target) {
        value += increment;
        counter.textContent = value; 
        setTimeout(update, 30); 
      } else {
        counter.textContent = target;
      }
    };
    update();
  });
});

function toggleMenu() {
  const nav = document.getElementById("nav-links");
  nav.classList.toggle("open");
}

window.addEventListener("resize", () => {
  const nav = document.getElementById("nav-links");
  if (window.innerWidth > 768) nav.classList.remove("open"); 
});

// Sélectionne tous les boutons de fermeture
    document.querySelectorAll('.btn-close').forEach(button => {
        button.addEventListener('click', function() {
            // Trouve le parent (.alert) et le supprime
            const alertBox = this.closest('.alert');
            if (alertBox) {
                alertBox.style.transition = "opacity 0.3s ease";
                alertBox.style.opacity = "0"; // Fondu
                setTimeout(() => alertBox.remove(), 300); // Suppression après le fondu
            }
        });
    });
