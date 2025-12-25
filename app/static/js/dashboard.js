const initDashboard = () => {
  document.addEventListener("DOMContentLoaded", () => {
    animateCounters();
    animateProgressBars();
    initProjetsChart();
  });
};

const animateCounters = () => {
  const counters = document.querySelectorAll(".big[data-count]");

  counters.forEach(counter => {
    const target = parseInt(counter.dataset.count, 10);
    if (!isNaN(target)) {
      counter.innerText = target;
    }
  });
};

const animateProgressBars = () => {
  const bars = document.querySelectorAll(".progress-fill[data-width]");

  bars.forEach(bar => {
    const width = parseFloat(bar.dataset.width);

    setTimeout(() => {
      bar.style.width = width + "%";
    }, 100);
  });
};

const initProjetsChart = () => {
  const ctx = document.getElementById("projetsChart");
  if (!ctx) return;

  try {
    const labels = JSON.parse(ctx.dataset.labels);
    const counts = JSON.parse(ctx.dataset.counts);

    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [{
          data: counts,
          backgroundColor: ['#bdc3c7', '#3498db', '#2ecc71', '#e74c3c'],
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: { display: false }
        }
      }
    });
  } catch (e) {
    console.error("Chart initialization error:", e);
  }
};

initDashboard();