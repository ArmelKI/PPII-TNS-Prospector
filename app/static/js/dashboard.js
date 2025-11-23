document.addEventListener("DOMContentLoaded", () => {
  // animation compteurs
  document.querySelectorAll("[data-count]").forEach(el => {
    const target = Number(el.dataset.count) || 0;
    let i = 0;
    const step = Math.max(1, Math.floor(target / 40));
    const tick = () => {
      i += step;
      if (i >= target) el.textContent = target;
      else {
        el.textContent = i;
        requestAnimationFrame(tick);
      }
    };
    tick();
  });

  // charts : si canvas présents, on initialise Chart.js
  // projets par statut
  const statutCtx = document.getElementById('projetsStatutChart');
  if (statutCtx) {
    const statutCounts = JSON.parse(statutCtx.dataset.counts || "{}");
    const labels = Object.keys(statutCounts);
    const data = Object.values(statutCounts);

    new Chart(statutCtx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data,
          backgroundColor: [
            '#0056b3','#4a8bed','#28a745','#ffb142','#cfd8dc','#607d8b'
          ],
          hoverOffset: 8,
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' },
          tooltip: { mode: 'index' }
        }
      }
    });
  }

  // disponibilite
  const dispoCtx = document.getElementById('dispoChart');
  if (dispoCtx) {
    const dispo = JSON.parse(dispoCtx.dataset.counts || "{}");
    const labels = Object.keys(dispo);
    const data = Object.values(dispo);

    new Chart(dispoCtx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          label: 'Disponibilité',
          data,
          backgroundColor: ['#28a745','#d32f2f'],
          borderRadius: 6
        }]
      },
      options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
  }

  // interactions (line)
  const interCtx = document.getElementById('interactionsChart');
  if (interCtx) {
    const labels = JSON.parse(interCtx.dataset.labels || "[]");
    const counts = JSON.parse(interCtx.dataset.counts || "[]");

    new Chart(interCtx, {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Interactions',
          data: counts,
          fill: true,
          borderColor: '#0056b3',
          backgroundColor: 'rgba(74,139,237,0.12)',
          tension: 0.25,
          pointRadius: 4
        }]
      },
      options: { responsive: true, scales: { y: { beginAtZero: true } } }
    });
  }
});
