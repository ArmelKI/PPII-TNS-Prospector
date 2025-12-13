let map;

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
        iconUrl: '../images/tns_logo.svg'
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
