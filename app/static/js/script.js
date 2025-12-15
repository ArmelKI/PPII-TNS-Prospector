/**
 * This script handles common front-end behaviors:
 * - Animated counters for stats or numbers
 * - Responsive mobile menu toggling
 * - Auto-closing the menu on window resize
 */

document.addEventListener("DOMContentLoaded", () => {
  // Animate all elements with a [data-count] attribute
  document.querySelectorAll("[data-count]").forEach(counter => {
    const target = +counter.dataset.count; // The final number to count up to
    let value = 0;
    const increment = Math.ceil(target / 40); // Controls animation speed

    /**
     * update()
     * Animates the counter by incrementing its value until it reaches the target.
     */
    const update = () => {
      if (value < target) {
        value += increment;
        counter.textContent = value; // Show the current value
        setTimeout(update, 30); // Schedule the next update
      } else {
        counter.textContent = target; // Ensure we end exactly at the target
      }
    };
    update();
  });
});

/**
 * toggleMenu()
 * Toggles the mobile navigation menu open or closed.
 * Called when the menu button is clicked.
 */
function toggleMenu() {
  const nav = document.getElementById("nav-links");
  nav.classList.toggle("open"); // Add or remove the 'open' class
}

/**
 * Automatically closes the mobile menu if the window is resized
 * to a width greater than 768px (i.e., desktop view).
 */
window.addEventListener("resize", () => {
  const nav = document.getElementById("nav-links");
  if (window.innerWidth > 768) nav.classList.remove("open"); // Hide menu on desktop
});
