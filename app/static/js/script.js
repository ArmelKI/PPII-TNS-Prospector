// Animation des compteurs du dashboard
document.addEventListener("DOMContentLoaded", () => {
  const counters = document.querySelectorAll("[data-count]");
  counters.forEach(counter => {
    const target = +counter.getAttribute("data-count");
    let count = 0;
    const speed = 30;
    const increment = Math.ceil(target / 40);

    const updateCount = () => {
      if (count < target) {
        count += increment;
        counter.textContent = count;
        setTimeout(updateCount, speed);
      } else {
        counter.textContent = target;
      }
    };
    updateCount();
  });
});

// Toggle mobile menu
function toggleMenu() {
    const navLinks = document.getElementById("nav-links");
    navLinks.style.display = navLinks.style.display === "none" || navLinks.style.display === "" ? "flex" : "none";
    navLinks.classList.toggle("open");
}

// Initialisation du menu burger au chargement de la page
document.addEventListener("DOMContentLoaded", () => {
    // Liaison du bouton burger avec la fonction toggleMenu
    const menuBurger = document.querySelector('.burger-menu');
    if (menuBurger) {
        menuBurger.addEventListener('click', toggleMenu);
    }
});

// Fermeture automatique du menu mobile quand on clique sur un lien
document.querySelectorAll('#nav-links a').forEach(link => {
  link.addEventListener('click', () => {
    const navLinks = document.getElementById("nav-links");
    if (window.innerWidth <= 768) { // Seulement en mode mobile
      navLinks.classList.remove("open");
      navLinks.style.display = "none";
    }
  });
});

// Ajustement du menu lors du redimensionnement de la fenêtre
window.addEventListener('resize', () => {
  const navLinks = document.getElementById("nav-links");
  if (window.innerWidth > 768) { // Mode desktop
    navLinks.style.display = "flex";
    navLinks.classList.remove("open");
  } else { // Mode mobile
    navLinks.style.display = "none";
  }
}); 

// Vérification initiale de l'affichage du menu au chargement de la page
window.addEventListener('load', () => {
  const navLinks = document.getElementById("nav-links");
  if (window.innerWidth > 768) {
    navLinks.style.display = "flex";
  } else {
    navLinks.style.display = "none";
  }
});


// =======================
// Graphique du dashboard 
// =======================
document.addEventListener("DOMContentLoaded", () => {
  const ctx = document.getElementById("statsChart");

  if (ctx) {
    // ... (le reste de votre code pour le graphique est correct) ...
    const nbClients = parseInt(document.querySelector("[data-count]:nth-child(1)")?.getAttribute("data-count")) || 0;
    const nbProjets = parseInt(document.querySelector("[data-count]:nth-child(2)")?.getAttribute("data-count")) || 0;
    const nbIntervenants = parseInt(document.querySelector("[data-count]:nth-child(3)")?.getAttribute("data-count")) || 0;

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Clients', 'Projets', 'Intervenants'],
        datasets: [{
          label: 'Statistiques globales',
          data: [nbClients, nbProjets, nbIntervenants],
          backgroundColor: [
            'rgba(0, 86, 179, 0.8)',     // bleu TNS
            'rgba(40, 167, 69, 0.8)',    // vert
            'rgba(255, 136, 0, 0.8)'     // orange
          ],
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        scales: {
          y: {
            beginAtZero: true,
            ticks: { stepSize: 1 }
          }
        },
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: 'Répartition des éléments',
            color: '#333',
            font: { size: 16, weight: 'bold' }
          }
        }
      }
    });
  }
});

// =======================
// Dialogues de confirmation
// =======================

/**
 * Demande confirmation avant de supprimer.
 * Appelée par 'onsubmit' sur les formulaires de suppression.
 */
function confirmDelete() {
  return confirm("Êtes-vous sûr de vouloir supprimer cet élément ?\nCette action est irréversible.");
}

/**
 * Demande confirmation avant de modifier.
 * Appelée par 'onsubmit' sur le formulaire de modification.
 */
function confirmModify() {
  return confirm("Êtes-vous sûr de vouloir enregistrer ces modifications ?");
}