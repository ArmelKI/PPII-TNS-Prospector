//Recherche rapide côté client
//  simple table search
function tableSearch(inputId, tableSelector) {
  const inp = document.getElementById(inputId);
  if (!inp) return;
  inp.addEventListener('input', () => {
    const q = inp.value.toLowerCase();
    document.querySelectorAll(tableSelector + ' tbody tr').forEach(row => {
      const text = row.textContent.toLowerCase();
      row.style.display = text.includes(q) ? '' : 'none';
    });
  });
}

document.addEventListener('DOMContentLoaded', () => {
  tableSearch('searchProjects', '.data-table');
  tableSearch('searchClients', '.data-table');
});
