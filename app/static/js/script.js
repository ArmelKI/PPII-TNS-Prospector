/*
script.js — comportements front-end communs

Contient :
- compteur animé
- menu mobile responsive
- fermeture automatique du menu
*/

document.addEventListener("DOMContentLoaded", () => {
  // Animation des compteurs
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

// Menu responsive
function toggleMenu() {
  const nav = document.getElementById("nav-links");
  nav.classList.toggle("open");
}

window.addEventListener("resize", () => {
  const nav = document.getElementById("nav-links");
  if (window.innerWidth > 768) nav.classList.remove("open");
});
