var map = L.map('map').setView([38.4375, -110.8125], 13);


let templateString = '/tile/{z}/{x}/{y}'

console.log(templateString);

L.tileLayer(templateString, {
    maxZoom: 19
  }).addTo(map);


// Poll for the rover's position every second
let roverMarker = new L.marker([0, 0]).addTo(map);
setInterval(() => {
    fetch("/roverCoords").then(res => res.json()).then(data => {
        console.log(data);
        roverMarker.setLatLng(data)
    })
}, 1000);



let pathMarkers = [];
let polyLine = new L.polyline(pathMarkers, {
    color: 'red',
    weight: 3,
    opacity: 0.5,
    smoothFactor: 1
}).addTo(map);

map.on("click", e => {
    let newMarker = new L.marker(e.latlng).addTo(map);
    pathMarkers.push(newMarker)
    console.log("lats",);
    polyLine.setLatLngs(pathMarkers.map(e => [e._latlng.lat, e._latlng.lng]))
    document.getElementById("pathOutput").innerText = pathMarkers.map(e => `${e._latlng.lat} ${e._latlng.lng}`).join("\n");
})



///////////////////////////////////
//
// Unit Conversion Stuff
//
//////////////////////////////////

function typeIndicator() {
    let coordinates = prompt("Enter coordinates in in lng, lat format");
    coordinates = coordinates.replace(" ", "");
    coordinates = coordinates.split(",");
    console.log(coordinates)
    let isConfirmed = confirm(`Add indicator at lng: ${coordinates[0]}, lat: ${coordinates[1]}?`);
    if (isConfirmed) {
        var marker = new L.marker(coordinates).addTo(map);
    }
}


function degMinSecToDecimal(deg, min, sec) {
    console.log("Converting:", deg, min, sec)
    console.log("Returning", (deg + (min / 60) + (sec / 3600)))
    return deg + (min / 60) + (sec / 3600);
}

function degDecimalMinToDecimal(deg, min) {
    return deg + (min / 60)
}

let open = false;

function openUnitConverter() {
    if (!open) {
        document.getElementById("unitConverter").style.display = "block";
        open = true;
    } else {
        closeUnitConverter();
    }

}
function closeUnitConverter() {
    document.getElementById("unitConverter").style.display = "none";
    open = false;
}

function updateConversionsBasedOn(el) {
    let sources = {
        "DMS": ["DMSDeg", "DMSMin", "DMSSec"],
        "DDM": ["DDMDeg", "DDMMin"],
        "Decimal": ["Decimal"]
    }

    let source = "DMS";
    if (el.id.indexOf("DMS") !== -1) source = "DMS"
    else if (el.id.indexOf("DDM") !== -1) source = "DDM"
    else if (el.id.indexOf("Decimal") !== -1) source = "Decimal";

    let sourceValues = [];
    for (let id of sources[source]) {
        console.log(document.getElementById(id))
        sourceValues.push(parseFloat(document.getElementById(id).value) || 0);
    }
    console.log("Source", sourceValues)

    let DMSValues = [];
    let DDMValues = [];
    let DecimalValue = 0;

    if (source === "DMS") {
        DMSValues = sourceValues;
        DecimalValue = degMinSecToDecimal(...sourceValues);
        console.log("Converted successfully: ", DecimalValue)
    } else if (source === "DDM") {
        DDMValues = sourceValues;
        DecimalValue = degDecimalMinToDecimal(...sourceValues);
        console.log("DDM convert", degDecimalMinToDecimal(...sourceValues))
    } else if (source === "Decimal") {
        DecimalValue = sourceValues;
    }

    console.log(DMSValues, DDMValues, DecimalValue)

    document.getElementById("DMSDeg").value = DMSValues[0] || "";
    document.getElementById("DMSMin").value = DMSValues[1] || "";
    document.getElementById("DMSSec").value = DMSValues[2] || "";

    document.getElementById("DDMDeg").value = DDMValues[0] || "";
    document.getElementById("DDMMin").value = DDMValues[1] || "";

    console.log("What is the problem", DecimalValue)
    document.getElementById("Decimal").value = DecimalValue;

}

Array.from(document.getElementsByClassName("convertInput")).forEach(el => {
    console.log(el)
    el.addEventListener("keyup", function (evt) {
        if (!isNaN(evt.key))
            updateConversionsBasedOn(el);
    });
})


let valuesCopied = [];
function copyCoords() {
    let el = document.getElementById("Decimal");
    el.select();
    el.setSelectionRange(0, 9999);
    valuesCopied.push(el.value);
    document.getElementById("saved").innerHTML +=
        `
    <p>${el.value}</p>
    `
    document.execCommand("copy")
}