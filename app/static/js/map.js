let map;
let searchCircle;
let prospectMarkers = [];
let clientMarkers = [];

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
    loadProspects();
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
    const marker = L.marker([client.lat, client.lng])
        .addTo(map);

    const popupContent = `
        <strong>${client.name}</strong><br>
        Secteur : ${client.secteur}<br>
        <button onclick="deleteClient(${client.id}, this)">Supprimer</button>
    `;

    marker.bindPopup(popupContent);

    clientMarkers.push({ id: client.id, marker: marker });
}


function addProspectMarker(p) {
    const marker = L.circleMarker([p.lat, p.lng], {
        radius: 6,
        color: 'blue',
        fillOpacity: 0.8
    }).addTo(map);

    const popupContent = `
        <strong>${p.name}</strong><br>
        Type : ${p.type}<br>
        Prospect OSM<br>
        <button onclick="addProspectToDB(${p.lat}, ${p.lng}, '${p.name}', '${p.type}')">
            Ajouter à ma liste de prospects
        </button>
    `;

    marker.bindPopup(popupContent);
    prospectMarkers.push(marker);
}

function clearProspectMarkers() {
    prospectMarkers.forEach(m => map.removeLayer(m));
    prospectMarkers = [];
}

function loadProspects() {
    clearProspectMarkers(); 

    const radius = document.getElementById("radius").value;

    drawRadius(48.66895, 6.15547, radius);

    fetch(`/map/${radius}`)
        .then(res => res.json())
        .then(prospects => {
            prospects.forEach(p => addProspectMarker(p));
        })
        .catch(err => console.error(err));
}

function addProspectToDB(lat, lng, name, type) {
    fetch('/map/add_prospect', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ lat, lng, name, type })
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert(`${name} ajouté à la BDD !`);
        } else {
            alert('Attention : ' + data.message);
        }
    })
    .catch(err => console.error(err));
}

function deleteClient(clientId, button) {
    if (!confirm("Voulez-vous vraiment supprimer ce client ?")) return;

    fetch(`/map/delete_client/${clientId}`, {
        method: 'DELETE'
    })
    .then(res => res.json())
    .then(data => {
        if (data.success) {
            alert("Client supprimé !");
            
            const clientData = clientMarkers.find(c => c.id === clientId);
            if (clientData) {
                map.removeLayer(clientData.marker);
                clientMarkers = clientMarkers.filter(c => c.id !== clientId);
            }
        } else {
            alert("Erreur : " + data.message);
        }
    })
    .catch(err => console.error(err));
}
