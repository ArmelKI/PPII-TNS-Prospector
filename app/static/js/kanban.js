document.addEventListener("DOMContentLoaded", () => {
  console.log("📋 Kanban JS loaded");
  
  const cards = document.querySelectorAll(".kanban-card");
  const columns = document.querySelectorAll(".kanban-column");
  let draggedItem = null;

  cards.forEach(card => {
    card.addEventListener("dragstart", function(e) {
      draggedItem = this;
      setTimeout(() => this.classList.add("dragging"), 0);
      console.log("Drag start:", this.dataset.id);
    });

    card.addEventListener("dragend", function() {
      this.classList.remove("dragging");
      draggedItem = null;
      columns.forEach(c => c.classList.remove("drag-over"));
    });
  });

  columns.forEach(column => {
    column.addEventListener("dragover", function(e) {
      e.preventDefault(); 
      this.classList.add("drag-over");
    });

    column.addEventListener("dragleave", function() {
      this.classList.remove("drag-over");
    });

    column.addEventListener("drop", async function(e) {
      e.preventDefault();
      this.classList.remove("drag-over");

      if (draggedItem) {
        const list = this.querySelector(".kanban-list");
        list.appendChild(draggedItem);

        const jalonId = draggedItem.dataset.id;
        const newStatut = this.dataset.statut; 

        console.log(`⚡ Drop detected! Jalon ${jalonId} to ${newStatut}`);

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