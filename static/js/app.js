document.addEventListener("DOMContentLoaded", () => {
  const searchForm = document.getElementById("search-form");

  if (searchForm) {
    searchForm.addEventListener("submit", function (event) {
      event.preventDefault();
      const nombre = document.getElementById("nombre").value;
      const genero = document.getElementById("genero").value;
      searchVideojuegos(nombre, genero);
    });
  }
});

function searchVideojuegos(nombre, genero) {
  const params = new URLSearchParams();
  if (nombre) params.append("nombre", nombre);
  if (genero) params.append("genero", genero);

  fetch(`/search?${params.toString()}`)
    .then((response) => response.json())
    .then((data) => {
      const resultsDiv = document.getElementById("search-results");
      resultsDiv.innerHTML = "<h2>Resultados de la búsqueda</h2>";
      data.forEach((v) => {
        resultsDiv.innerHTML += `<p>${v.nombre} - ${v.genero} - ${v.plataforma}</p>`;
      });
    })
    .catch((error) => console.error("Error:", error));
}

function fetchLists() {
  fetch("/list") // Asumiendo que esta ruta devuelve todas las listas
    .then((response) => response.json())
    .then((data) => {
      const resultsDiv = document.getElementById("lists-results");
      resultsDiv.innerHTML = "<h2>Mis Listas</h2>";
      data.forEach((list) => {
        resultsDiv.innerHTML += `<p><a href="listid.html?nombre=${list.nombre}">${list.nombre}</a></p>`;
      });
    })
    .catch((error) => console.error("Error:", error));
}

function fetchListDetails(nombreLista) {
  const params = new URLSearchParams();
  params.append("nombre", nombreLista);

  fetch(`/list?${params.toString()}`)
    .then((response) => response.json())
    .then((data) => {
      const detailsDiv = document.getElementById("list-details");
      detailsDiv.innerHTML = `<h2>Lista: ${data.nombre}</h2>`;
      data.videojuegos.forEach((v) => {
        detailsDiv.innerHTML += `<p>${v.nombre} - ${v.genero} - ${v.plataforma}</p>`;
      });
    })
    .catch((error) => console.error("Error:", error));
}
