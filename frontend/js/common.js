// ===================== FUNCȚII COMUNE PENTRU TOATE PAGINILE =====================

// Dacă pagina e servită de FastAPI (http://127.0.0.1:8000/) folosim căi relative;
// dacă e deschisă direct din fișier sau din Live Server, apelăm backend-ul local.
const API_BASE = window.location.port === "8000" ? "" : "http://127.0.0.1:8000";

const FALLBACK_IMG =
    "data:image/svg+xml;charset=UTF-8," +
    encodeURIComponent(
        '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="500">' +
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0" stop-color="#4facfe"/><stop offset="1" stop-color="#00c6a7"/></linearGradient></defs>' +
        '<rect width="800" height="500" fill="url(#g)"/>' +
        '<text x="400" y="265" font-family="Arial" font-size="40" fill="white" text-anchor="middle">Travel Agency Project</text></svg>'
    );

// Protecție XSS: orice text venit din server trece prin escapeHtml înainte de innerHTML
function escapeHtml(value) {
    return String(value ?? "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

// "2026-11-24" -> "24.11.2026"
function formatDate(isoDate) {
    if (!isoDate) return "-";
    const [y, m, d] = isoDate.split("-");
    return `${d}.${m}.${y}`;
}

function nightsBetween(isoStart, isoEnd) {
    return Math.round((new Date(isoEnd) - new Date(isoStart)) / 86400000);
}

function formatPrice(value) {
    return Number(value).toLocaleString("ro-RO", { maximumFractionDigits: 0 }) + " €";
}

function stars(count) {
    return "★".repeat(count);
}

function imgTag(offer) {
    return `<img src="${escapeHtml(offer.image_url || FALLBACK_IMG)}" alt="${escapeHtml(offer.hotel_name)}"
                 loading="lazy" onerror="this.onerror=null; this.src=FALLBACK_IMG;">`;
}

function offerUrl(offerId, persons) {
    return `oferta.html?${new URLSearchParams({ id: offerId, persons: persons || 1 })}`;
}

async function apiRequest(path, options = {}) {
    const response = await fetch(API_BASE + path, {
        headers: { "Content-Type": "application/json" },
        ...options,
    });
    let body = null;
    try {
        body = await response.json();
    } catch (_) {
        /* răspuns fără JSON */
    }
    if (!response.ok) {
        let message = "A apărut o eroare. Încearcă din nou.";
        if (body && typeof body.detail === "string") message = body.detail;
        else if (response.status === 422) message = "Datele introduse nu sunt valide. Verifică formularul.";
        const error = new Error(message);
        error.status = response.status;
        throw error;
    }
    return body;
}

// Calendare Flatpickr: valoarea trimisă e ISO (Y-m-d), utilizatorul vede d.m.Y
function initDatePickers(depSelector, retSelector) {
    // Dacă CDN-ul Flatpickr nu se încarcă, folosim calendarul nativ al browserului
    if (typeof flatpickr === "undefined") {
        const today = new Date().toISOString().slice(0, 10);
        const nativePicker = selector => {
            const input = document.querySelector(selector);
            input.type = "date";
            input.min = today;
            return {
                setDate: value => (input.value = value),
                set: (_, value) => (input.min = value),
                clear: () => (input.value = ""),
                selectedDates: [],
            };
        };
        return { depPicker: nativePicker(depSelector), retPicker: nativePicker(retSelector) };
    }

    const common = { locale: "ro", dateFormat: "Y-m-d", altInput: true, altFormat: "d.m.Y", minDate: "today" };
    const retPicker = flatpickr(retSelector, common);
    const depPicker = flatpickr(depSelector, {
        ...common,
        onChange: ([selected]) => {
            // Data întoarcerii nu poate fi înaintea plecării
            retPicker.set("minDate", selected || "today");
            if (selected && retPicker.selectedDates[0] && retPicker.selectedDates[0] <= selected) {
                retPicker.clear();
            }
        },
    });
    return { depPicker, retPicker };
}

function readSearchForm(ids) {
    return {
        destination: document.getElementById(ids.destination).value.trim(),
        departure_city: document.getElementById(ids.departureCity).value.trim(),
        departure_date: document.getElementById(ids.departureDate).value,
        return_date: document.getElementById(ids.returnDate).value,
        persons: document.getElementById(ids.persons).value,
    };
}
