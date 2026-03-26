let map;
let marker;
let allMarkers = [];

async function initMap() {
    // google maps is loaded async via inline script in head which adds it to window
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    const defaultLocation = { lat: 12.9716, lng: 77.5946 }; // Bengaluru

    map = new Map(document.getElementById("map"), {
        zoom: 12,
        center: defaultLocation,
        mapId: "DEMO_MAP_ID",
    });

    map.addListener("click", (e) => {
        placeMarker(e.latLng, AdvancedMarkerElement);
    });

    document.getElementById("btn-my-location").addEventListener("click", () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (position) => {
                    const pos = { lat: position.coords.latitude, lng: position.coords.longitude };
                    map.setCenter(pos);
                    map.setZoom(16);
                    placeMarker(pos, AdvancedMarkerElement);
                },
                () => alert("Error: The Geolocation service failed.")
            );
        } else {
            alert("Error: Your browser doesn't support geolocation.");
        }
    });

    document.getElementById("btn-clear-pin").addEventListener("click", () => {
        if (marker) {
            marker.map = null;
            marker = null;
            document.getElementById("form-lat").value = "";
            document.getElementById("form-lng").value = "";
            document.getElementById("coords-display").innerText = "Click on the map to select location";
        }
    });

    fetchAndLogReports(AdvancedMarkerElement);
}

function placeMarker(latLng, AdvancedMarkerElement) {
    if (marker) marker.map = null;
    
    const pin = document.createElement("div");
    pin.innerHTML = "📍";
    pin.style.fontSize = "38px";
    pin.style.cursor = "pointer";
    pin.style.transform = "translateY(-50%)";

    marker = new AdvancedMarkerElement({
        position: latLng,
        map: map,
        title: "Selected Location",
        gmpDraggable: true,
        content: pin
    });

    updateFormCoords(marker.position.lat, marker.position.lng);

    marker.addListener("dragend", () => {
        updateFormCoords(marker.position.lat, marker.position.lng);
    });
}

function updateFormCoords(lat, lng) {
    const latitude = typeof lat === 'function' ? lat() : lat;
    const longitude = typeof lng === 'function' ? lng() : lng;
    
    document.getElementById("form-lat").value = latitude;
    document.getElementById("form-lng").value = longitude;
    document.getElementById("coords-display").innerText = `Lat: ${latitude.toFixed(5)}, Lng: ${longitude.toFixed(5)}`;
}

async function fetchAndLogReports(AdvancedMarkerElement) {
    try {
        const response = await fetch('/api/reports');
        const reports = await response.json();
        renderTable(reports);
        
        allMarkers.forEach(m => m.map = null);
        allMarkers = [];

        reports.forEach(report => {
            const pinColor = report.status === "Resolved" ? "#10b981" : "#ef4444"; 
            const pinSvg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            pinSvg.setAttribute("width", "36");
            pinSvg.setAttribute("height", "45");
            pinSvg.setAttribute("viewBox", "0 0 24 30");
            pinSvg.innerHTML = `<path fill="${pinColor}" d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>`;

            const wrapper = document.createElement("div");
            wrapper.style.filter = "drop-shadow(0px 4px 4px rgba(0,0,0,0.25))";
            wrapper.style.cursor = "pointer";
            wrapper.style.transition = "transform 0.2s";
            wrapper.onmouseover = () => { wrapper.style.transform = "scale(1.1) translateY(-4px)"; };
            wrapper.onmouseout = () => { wrapper.style.transform = "scale(1) translateY(0)"; };
            wrapper.appendChild(pinSvg);

            const m = new AdvancedMarkerElement({
                position: { lat: report.lat, lng: report.lng },
                map: map,
                title: report.description || "Reported Spot",
                content: wrapper
            });

            m.addListener("click", () => {
                if (report.status === "Pending") {
                    document.getElementById("resolve-container").style.display = "block";
                    document.getElementById("resolve-spot-id").innerText = report.id;
                    document.getElementById("resolve-id-input").value = report.id;
                    document.getElementById("resolve-container").scrollIntoView({ behavior: "smooth", block: "center" });
                } else {
                    alert(`Report #${report.id} is already resolved!`);
                }
            });

            allMarkers.push(m);
        });
    } catch (e) {
        console.error("Failed to fetch reports:", e);
    }
}

function renderTable(reports) {
    const tbody = document.querySelector("#reports-table tbody");
    tbody.innerHTML = "";
    const filter = document.getElementById("status-filter").value;

    reports.forEach(r => {
        if (filter !== "All" && r.status !== filter) return;
        
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>#${r.id}</td>
            <td>${new Date(r.created_at).toLocaleDateString()}</td>
            <td>${r.lat.toFixed(4)}, ${r.lng.toFixed(4)}</td>
            <td><span class="badge ${r.status.toLowerCase()}">${r.status}</span></td>
            <td><a href="/static/uploads/${r.before_image}" target="_blank" class="action-link">View Image</a></td>
            <td>${r.after_image ? `<a href="/static/uploads/${r.after_image}" target="_blank" class="action-link">View After</a>` : '-'}</td>
            <td>
                ${r.status === 'Pending' 
                    ? `<button class="btn btn-secondary btn-sm resolve-btn" data-id="${r.id}" style="padding: 0.3rem 0.6rem; font-size: 0.85rem;">Resolve</button>` 
                    : '<span style="color:var(--success); font-weight:600;">Completed</span>'}
            </td>
        `;
        tbody.appendChild(tr);
    });

    document.querySelectorAll(".resolve-btn").forEach(btn => {
        btn.addEventListener("click", (e) => {
            const reportId = e.target.getAttribute("data-id");
            document.getElementById("resolve-container").style.display = "block";
            document.getElementById("resolve-spot-id").innerText = reportId;
            document.getElementById("resolve-id-input").value = reportId;
            document.getElementById("resolve-container").scrollIntoView({ behavior: "smooth", block: "center" });
        });
    });
}

window.onload = () => {
    initMap();
};

document.getElementById("report-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    if (!formData.get("lat") || !formData.get("lng")) {
        alert("Please select a location on the map first!");
        return;
    }
    
    const submitBtn = e.target.querySelector(".submit-btn");
    submitBtn.innerText = "Submitting...";
    submitBtn.disabled = true;

    try {
        const response = await fetch("/api/reports", {
            method: "POST",
            body: formData
        });
        
        if (response.ok) {
            alert("Report submitted successfully! Thank you for helping keep Bengaluru clean.");
            e.target.reset();
            if (marker) { marker.map = null; marker = null; }
            document.getElementById("coords-display").innerText = "Click on the map to select location";
            
            const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
            fetchAndLogReports(AdvancedMarkerElement);
        } else {
            const err = await response.json();
            alert("Error: " + err.error);
        }
    } catch(err) {
        alert("Failed to submit report.");
    } finally {
        submitBtn.innerText = "Submit Report";
        submitBtn.disabled = false;
    }
});

document.getElementById("resolve-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    const reportId = document.getElementById("resolve-id-input").value;
    
    const submitBtn = e.target.querySelector(".submit-btn");
    submitBtn.innerText = "Resolving...";
    submitBtn.disabled = true;

    try {
        const response = await fetch(`/api/reports/${reportId}/resolve`, {
            method: "POST",
            body: formData
        });
        
        if (response.ok) {
            alert("Report marked as resolved!");
            e.target.reset();
            document.getElementById("resolve-container").style.display = "none";
            const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
            fetchAndLogReports(AdvancedMarkerElement);
        } else {
            const err = await response.json();
            alert("Error: " + err.error);
        }
    } catch(err) {
        alert("Failed to resolve report.");
    } finally {
        submitBtn.innerText = "Verify & Resolve";
        submitBtn.disabled = false;
    }
});

document.getElementById("btn-cancel-resolve").addEventListener("click", () => {
    document.getElementById("resolve-container").style.display = "none";
    document.getElementById("resolve-form").reset();
});

document.getElementById("status-filter").addEventListener("change", async () => {
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");
    fetchAndLogReports(AdvancedMarkerElement);
});
