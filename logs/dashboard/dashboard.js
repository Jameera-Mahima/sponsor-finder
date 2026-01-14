// Sponsor Finder - Live Dashboard Updates

let currentCampaignId = null;
let updateInterval = null;
let startTime = null;

// Load current execution data
async function loadCurrentExecution() {
    try {
        const response = await fetch('../current_execution.json');

        if (!response.ok) {
            // No active execution
            setIdleState();
            return;
        }

        const data = await response.json();

        if (data.campaign_id !== currentCampaignId) {
            currentCampaignId = data.campaign_id;
            startTime = new Date(data.start_time);
            resetDashboard();
        }

        updateDashboard(data);
        updateElapsedTime();
        updateLastRefresh();
    } catch (error) {
        console.error('Failed to load execution data:', error);
        setIdleState();
    }
}

// Set dashboard to idle state
function setIdleState() {
    document.getElementById('current-status').textContent = '⏸️ Idle';
    document.getElementById('current-status').className = '';
    document.getElementById('campaign-name').textContent = '-';
    document.getElementById('campaign-id').textContent = '-';
    document.getElementById('current-phase').textContent = '-';
    document.getElementById('current-agent').textContent = '-';
}

// Update dashboard with new data
function updateDashboard(data) {
    // Update status
    const statusEl = document.getElementById('current-status');
    statusEl.textContent = `${getStatusIcon(data.status)} ${formatStatus(data.status)}`;
    statusEl.className = data.status.replace('_', '-');

    // Update campaign info
    document.getElementById('campaign-name').textContent = data.campaign_name || '-';
    document.getElementById('campaign-id').textContent = data.campaign_id || '-';
    document.getElementById('current-phase').textContent = data.current_phase || '-';
    document.getElementById('current-agent').textContent = data.current_agent || '-';

    // Update metrics
    if (data.summary) {
        document.getElementById('total-tokens').textContent =
            (data.summary.total_tokens_used || 0).toLocaleString();
        document.getElementById('total-api-calls').textContent =
            data.summary.total_api_calls || 0;
        document.getElementById('total-cost').textContent =
            `$${(data.summary.estimated_cost_usd || 0).toFixed(2)}`;
        document.getElementById('sponsors-found').textContent =
            data.summary.sponsors_found || 0;
    }

    // Update phase progress
    if (data.phases && data.phases.length > 0) {
        renderPhases(data.phases);
    }

    // Update log stream
    if (data.recent_logs && data.recent_logs.length > 0) {
        renderLogStream(data.recent_logs);
    }

    // Update errors
    if (data.errors && data.errors.length > 0) {
        renderErrors(data.errors, data.warnings || []);
    } else {
        document.getElementById('errors-container').innerHTML =
            '<p class="no-errors">✅ No errors</p>';
    }
}

// Get status icon
function getStatusIcon(status) {
    const icons = {
        'in_progress': '🔄',
        'completed': '✅',
        'failed': '❌',
        'partial': '⚠️',
        'idle': '⏸️'
    };
    return icons[status] || '❓';
}

// Format status text
function formatStatus(status) {
    return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Reset dashboard
function resetDashboard() {
    document.getElementById('phases-container').innerHTML = '';
    document.getElementById('log-stream').innerHTML = '';
}

// Render phases
function renderPhases(phases) {
    const container = document.getElementById('phases-container');
    container.innerHTML = '';

    phases.forEach((phase, index) => {
        const phaseEl = document.createElement('div');
        phaseEl.className = `phase-item ${phase.status}`;

        const statusIcon = getStatusIcon(phase.status);
        const duration = phase.duration_seconds
            ? `(${formatDuration(phase.duration_seconds)})`
            : '';

        phaseEl.innerHTML = `
            <div class="phase-header">
                <span>${statusIcon} Phase ${phase.phase_number}: ${phase.phase_name}</span>
                <span>${duration}</span>
            </div>
            <div class="phase-agents">
                Agents: ${phase.agents_executed.join(', ') || 'None'}
            </div>
            ${phase.status === 'completed' && phase.outputs_produced ? `
                <div class="phase-agents">
                    Outputs: ${phase.outputs_produced.length} files
                </div>
            ` : ''}
        `;

        container.appendChild(phaseEl);
    });
}

// Render log stream
function renderLogStream(logs) {
    const container = document.getElementById('log-stream');
    container.innerHTML = '';

    // Show last 10 logs
    logs.slice(-10).forEach(log => {
        const logEl = document.createElement('div');
        logEl.className = `log-entry ${log.severity || ''}`;

        const timestamp = new Date(log.timestamp).toLocaleTimeString();

        logEl.innerHTML = `
            <span class="log-time">${timestamp}</span>
            <strong>${log.agent}:</strong> ${log.message}
        `;

        container.appendChild(logEl);
    });

    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;
}

// Render errors and warnings
function renderErrors(errors, warnings) {
    const container = document.getElementById('errors-container');
    container.innerHTML = '';

    [...errors, ...warnings].forEach(item => {
        const errorEl = document.createElement('div');
        errorEl.className = item.severity === 'error' ? 'error-item' : 'warning-item';

        const timestamp = new Date(item.timestamp).toLocaleTimeString();

        errorEl.innerHTML = `
            <div class="error-severity">${item.severity}: ${item.error_type || 'Unknown'}</div>
            <div>${item.message}</div>
            <div style="font-size: 12px; color: #666; margin-top: 5px;">
                ${timestamp} - Agent: ${item.agent} - Phase: ${item.phase}
            </div>
            ${item.resolution ? `<div style="font-size: 12px; margin-top: 5px; color: #6bcf7f;">
                ✓ Resolved: ${item.resolution}
            </div>` : ''}
        `;

        container.appendChild(errorEl);
    });
}

// Format duration in seconds to human-readable
function formatDuration(seconds) {
    if (seconds < 60) {
        return `${seconds}s`;
    }
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
}

// Update elapsed time
function updateElapsedTime() {
    if (!startTime) return;

    const now = new Date();
    const elapsedSeconds = Math.floor((now - startTime) / 1000);
    const minutes = Math.floor(elapsedSeconds / 60);
    const seconds = elapsedSeconds % 60;

    document.getElementById('elapsed-time').textContent =
        `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Update last refresh timestamp
function updateLastRefresh() {
    const now = new Date();
    document.getElementById('last-update').textContent = now.toLocaleTimeString();
}

// Auto-refresh every 2 seconds during execution
function startMonitoring() {
    // Initial load
    loadCurrentExecution();

    // Set up interval for updates
    updateInterval = setInterval(() => {
        loadCurrentExecution();
    }, 2000);

    // Update elapsed time every second
    setInterval(updateElapsedTime, 1000);
}

// Stop monitoring (for cleanup)
function stopMonitoring() {
    if (updateInterval) {
        clearInterval(updateInterval);
        updateInterval = null;
    }
}

// Initialize dashboard on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('Sponsor Finder Dashboard initialized');
    startMonitoring();
});

// Clean up on page unload
window.addEventListener('beforeunload', () => {
    stopMonitoring();
});
