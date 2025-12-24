// preview image
function previewImage(input, previewSelector) {
  const preview = document.querySelector(previewSelector);
  if (!input.files || !input.files[0]) return;
  const reader = new FileReader();
  reader.onload = e => preview.src = e.target.result;
  reader.readAsDataURL(input.files[0]);
}

document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("form[data-ajax]").forEach(form => {
    form.addEventListener("submit", async (ev) => {
      ev.preventDefault();
      const fd = new FormData(form);
      const url = form.action;
      const res = await fetch(url, { method: 'POST', body: fd });
      const data = await res.json();
      if (res.ok) {
        alert("Upload OK");
        location.reload();
      } else {
        alert("Erreur: " + (data.error || res.statusText));
      }
    });
  });
});
