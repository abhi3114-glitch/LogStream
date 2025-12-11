const MAX_LOGS = 1000;
let logs = [];
let ws;
let isConnected = false;
let filters = {
    query: "",
    level: "",
    service: ""
};

const logContainer = document.getElementById('log-container');
const connectionStatus = document.getElementById('connection-status');
const connectionDot = document.getElementById('connection-dot');
const logCountEl = document.getElementById('log-count');

function connect() {
    // Determine protocol (ws or wss)
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws`);

    ws.onopen = () => {
        isConnected = true;
        updateStatus("Live", true);
        // Request initial history
        sendFilterUpdate();
    };

    ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        if (message.type === "new_log") {
            addLogToUI(message.data);
        } else if (message.type === "history") {
            // Clear current logs and load history
            clearLogs();
            message.data.forEach(log => addLogToUI(log, false)); // false = append to end (history usually sorted desc)
        }
    };

    ws.onclose = () => {
        isConnected = false;
        updateStatus("Reconnecting...", false);
        setTimeout(connect, 3000);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        ws.close();
    };
}

function updateStatus(text, connected) {
    connectionStatus.textContent = text;
    if (connected) {
        connectionDot.classList.add('connected');
    } else {
        connectionDot.classList.remove('connected');
    }
}

function sendFilterUpdate() {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({
            type: "update_filters",
            filters: filters
        }));
    }
}

function addLogToUI(log, prepend = true) {
    const el = document.createElement('div');
    el.className = 'log-entry';

    // Trim timestamp to HH:mm:ss.mss
    const time = log.timestamp.split('T')[1].slice(0, 12);

    el.innerHTML = `
        <span class="log-ts">${time}</span>
        <span class="log-level level-${log.level}">${log.level}</span>
        <span class="log-service">[${log.service}]</span>
        <span class="log-msg">${escapeHtml(log.raw)}</span>
    `;

    if (prepend) {
        logContainer.insertBefore(el, logContainer.firstChild);
    } else {
        logContainer.appendChild(el);
    }

    // Prune entries
    if (logContainer.children.length > MAX_LOGS) {
        logContainer.removeChild(logContainer.lastChild);
    }

    updateStats();
}

function clearLogs() {
    logContainer.innerHTML = '';
    updateStats();
}

function updateStats() {
    logCountEl.textContent = logContainer.children.length;
}

function escapeHtml(text) {
    if (!text) return "";
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Event Listeners
document.getElementById('search-input').addEventListener('input', (e) => {
    filters.query = e.target.value;
    debounce(sendFilterUpdate, 300)();
});

document.getElementById('level-select').addEventListener('change', (e) => {
    filters.level = e.target.value;
    clearLogs();
    sendFilterUpdate();
});

document.getElementById('service-input').addEventListener('input', (e) => {
    filters.service = e.target.value;
    debounce(sendFilterUpdate, 300)();
});

// Utility: Debounce
let debounceTimer;
function debounce(func, delay) {
    return function () {
        const context = this;
        const args = arguments;
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => func.apply(context, args), delay);
    }
}

// Start
connect();
