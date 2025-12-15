document.addEventListener("DOMContentLoaded", () => {
  console.log("📋 Kanban JS loaded");
  
  const cards = document.querySelectorAll(".kanban-card");
  const columns = document.querySelectorAll(".kanban-column");
  let draggedItem = null;

  // --- 1. CARD management (What we move) ---
  cards.forEach(card => {
    card.addEventListener("dragstart", function(e) {
      draggedItem = this;
      setTimeout(() => this.classList.add("dragging"), 0);
      console.log("Drag start:", this.dataset.id);
    });

    card.addEventListener("dragend", function() {
      this.classList.remove("dragging");
      draggedItem = null;
      // Visual cleanup of columns
      columns.forEach(c => c.classList.remove("drag-over"));
    });
  });

  // --- 2. COLUMN management (Where we drop) ---
  columns.forEach(column => {
    column.addEventListener("dragover", function(e) {
      e.preventDefault(); // REQUIRED to allow drop
      this.classList.add("drag-over");
    });

    column.addEventListener("dragleave", function() {
      this.classList.remove("drag-over");
    });

    column.addEventListener("drop", async function(e) {
      e.preventDefault();
      this.classList.remove("drag-over");

      if (draggedItem) {
        // Visual part: Move the card into the column's list
        const list = this.querySelector(".kanban-list");
        list.appendChild(draggedItem);

        // Data part: Get the IDs
        const jalonId = draggedItem.dataset.id;
        // Use 'this' which is the column
        const newStatut = this.dataset.statut; 

        console.log(`⚡ Drop detected! Jalon ${jalonId} to ${newStatut}`);

        // Server part (AJAX)
        try {
          const response = await fetch("/jalons/api/update_statut", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              id_jalon: jalonId,
              nouveau_statut: newStatut
            })
          });
          
          const res = await response.json();
          if(res.success) {
            console.log("✅ Save OK");
          } else {
            alert("Save error: " + res.error);
          }
        } catch (err) {
          console.error(err);
          alert("Network error (check the console)");
        }
      }
    });
  });
});