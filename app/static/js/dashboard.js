/**
 * Initialize dashboard behaviors once DOM is ready.
 *
 * Sets up counters, animated progress bars, and the Chart.js chart.
 */
const initDashboard = () => {
  // Wait for DOM to be fully parsed before touching elements
  document.addEventListener("DOMContentLoaded", () => {
    animateCounters();
    animateProgressBars();
    initProjetsChart();
  });
};

/**
 * Animate numeric counters by reading a data-count attribute and updating the text.
 *
 * This simply ensures the displayed value matches the data attribute. If you want
 * a smoother counting animation later, this is the place to implement it.
 */
const animateCounters = () => {
  const counters = document.querySelectorAll(".big[data-count]");

  counters.forEach(counter => {
    // Parse the intended final value; ignore invalid numbers
    const target = parseInt(counter.dataset.count, 10);
    if (!isNaN(target)) {
      // Directly set the displayed number for now (keeps VS Code previews consistent)
      counter.innerText = target;
    }
  });
};

/**
 * Apply widths to progress bar fill elements using their data-width attribute.
 *
 * A short timeout gives a simple CSS transition some time to run, producing a
 * smooth visual fill effect rather than an immediate jump.
 */
const animateProgressBars = () => {
  const bars = document.querySelectorAll(".progress-fill[data-width]");

  bars.forEach(bar => {
    // Use parseFloat to accept decimal percentages like "75.5"
    const width = parseFloat(bar.dataset.width);

    // Small delay so CSS transitions can animate the width change
    setTimeout(() => {
      // Set inline style to trigger the transition defined in CSS
      bar.style.width = width + "%";
    }, 100);
  });
};

/**
 * Initialize the Chart.js doughnut chart for project statistics.
 *
 * Reads JSON-encoded labels and counts from data attributes on the canvas element.
 * If parsing fails, logs an error instead of throwing, so the rest of the page keeps working.
 */
const initProjetsChart = () => {
  const ctx = document.getElementById("projetsChart");
  if (!ctx) return;

  try {
    // Parse JSON strings embedded in data attributes
    const labels = JSON.parse(ctx.dataset.labels);
    const counts = JSON.parse(ctx.dataset.counts);

    // Create a doughnut chart with a cutout for a donut-like appearance
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
    // Keep the page functional and help debugging if the embedded JSON is malformed
    console.error("Chart initialization error:", e);
  }
};

// Start everything
initDashboard();