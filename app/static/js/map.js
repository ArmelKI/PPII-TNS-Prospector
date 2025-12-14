let map;
let searchCircle;
let prospectMarkers = [];

function drawRadius(lat, lng, radius) {
    if (searchCircle) {
        map.removeLayer(searchCircle);
    }

    searchCircle = L.circle([lat, lng], {
        radius: radius,
        color: 'red',
        fillColor: 'red',
        fillOpacity: 0.2
    }).addTo(map);

    map.fitBounds(searchCircle.getBounds());
}

function init() {
    console.log("init");

    const TN = {
        lat: 48.66895,
        lng: 6.15547
    };
    const zoomLevel = 15;

    map = L.map("mapid").setView([TN.lat, TN.lng], zoomLevel);

    L.tileLayer(
        'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap'
        }
    ).addTo(map);

    const myIconClass = L.Icon.extend({
        options: {
            iconSize: [60, 35],
            iconAnchor: [10, 10],
            popupAnchor: [0, -10]
        }
    });

    const icon = new myIconClass({
        iconUrl: '../static/images/tns_logo.svg'
    });

    L.marker([TN.lat, TN.lng], { icon })
        .addTo(map)
        .bindPopup('TNS');

    loadClients();
}

function loadClients() {
    fetch("/map/api")
        .then(response => response.json())
        .then(clients => {
            console.log("Clients reçus :", clients);

            clients.forEach(client => {
                addClientMarker(client);
            });
        })
        .catch(error => {
            console.error("Erreur API clients :", error);
        });
}

function addClientMarker(client) {
    L.marker([client.lat, client.lng])
        .addTo(map)
        .bindPopup(`
            <strong>${client.name}</strong><br>
            Secteur : ${client.id}
        `);
}

function addProspectMarker(p) {
    const marker = L.circleMarker([p.lat, p.lng], {
        radius: 6,
        color: 'blue',
        fillOpacity: 0.8
    }).addTo(map)
      .bindPopup(`
        <strong>${p.name}</strong><br>
        Secteur (EN) : ${p.type}<br>
        Prospect OSM
    `);

    prospectMarkers.push(marker);
}

function clearProspectMarkers() {
    prospectMarkers.forEach(m => map.removeLayer(m)); // supprime chaque marqueur
    prospectMarkers = []; // vide le tableau
}

function loadProspects() {
    clearProspectMarkers(); // supprime les anciens avant d'ajouter les nouveaux

    const radius = document.getElementById("radius").value;

    drawRadius(48.66895, 6.15547, radius);

    fetch(`/map/${radius}`)
        .then(res => res.json())
        .then(prospects => {
            prospects.forEach(p => addProspectMarker(p));
        })
        .catch(err => console.error(err));
}
