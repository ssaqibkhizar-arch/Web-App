// ==========================================================================
// DOM Element Caching
// ==========================================================================
const DOM = {
    inputs: {
        rows: document.getElementById('grid-rows'),
        cols: document.getElementById('grid-cols')
    },
    buttons: {
        init: document.getElementById('btn-init'),
        reset: document.getElementById('btn-reset'),
        step: document.getElementById('btn-step')
    },
    metrics: {
        status: document.getElementById('status-display'),
        position: document.getElementById('position-display'),
        percepts: document.getElementById('percepts-display'),
        inference: document.getElementById('inference-display')
    },
    gridContainer: document.getElementById('wumpus-grid')
};

// ==========================================================================
// State Management
// ==========================================================================
let currentRows = 4;
let currentCols = 4;

// ==========================================================================
// API Interaction & Logic
// ==========================================================================

/**
 * Initializes the backend environment and sets up the frontend empty grid.
 */
async function initializeEnvironment() {
    currentRows = parseInt(DOM.inputs.rows.value) || 4;
    currentCols = parseInt(DOM.inputs.cols.value) || 4;

    try {
        DOM.metrics.status.innerText = "Initializing Server...";
        
        const response = await fetch('/init', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ rows: currentRows, cols: currentCols })
        });
        
        const data = await response.json();

        if (data.status === "initialized") {
            // Update UI State
            DOM.metrics.status.innerText = "Active - Awaiting Move";
            DOM.metrics.status.style.color = "#10b981"; // Green
            DOM.metrics.position.innerText = `[${data.agent_pos[0]}, ${data.agent_pos[1]}]`;
            DOM.metrics.percepts.innerText = "None";
            DOM.metrics.inference.innerText = "0";

            // Enable/Disable Controls
            DOM.buttons.step.disabled = false;
            DOM.buttons.reset.disabled = false;

            // Render Initial Empty Grid (All unknown except start)
            renderGrid(null); // null data means draw empty
        }
    } catch (error) {
        console.error("Initialization failed:", error);
        DOM.metrics.status.innerText = "Error: Backend unreachable";
        DOM.metrics.status.style.color = "#ef4444"; // Red
    }
}

/**
 * Commands the agent to evaluate its knowledge base and make one move.
 */
async function takeNextStep() {
    try {
        DOM.metrics.status.innerText = "Computing Resolution...";
        DOM.buttons.step.disabled = true; // Disable briefly to prevent spam-clicking
        
        const response = await fetch('/step', { method: 'POST' });
        const data = await response.json();

        if (data.error) {
            alert(data.error);
            DOM.metrics.status.innerText = "Error Occurred";
            return;
        }

        // Update Metrics Dashboard
        DOM.metrics.inference.innerText = data.inference_steps;
        DOM.metrics.percepts.innerText = data.percepts.length > 0 ? data.percepts.join(', ') : "None";
        
        // Update Grid UI
        renderGrid(data.grid);

        // Check Agent State
        if (data.agent_pos) {
            DOM.metrics.position.innerText = `[${data.agent_pos[0]}, ${data.agent_pos[1]}]`;
            DOM.metrics.status.innerText = "Move Successful";
            DOM.buttons.step.disabled = false; // Re-enable for next move
        } else {
            DOM.metrics.position.innerText = "Halted";
            DOM.metrics.status.innerText = "Halted - No Safe Moves Left";
            DOM.metrics.status.style.color = "#facc15"; // Yellow warning
            DOM.buttons.step.disabled = true; // Keep disabled
        }

    } catch (error) {
        console.error("Step failed:", error);
        DOM.metrics.status.innerText = "Error during inference";
    }
}

// ==========================================================================
// UI Rendering
// ==========================================================================

/**
 * Draws the grid elements based on the dimensions and state array.
 * @param {Array<Array<string>> | null} gridData - 2D array of cell states from backend.
 */
function renderGrid(gridData) {
    // Set dynamic CSS Grid columns based on user input
    DOM.gridContainer.style.gridTemplateColumns = `repeat(${currentCols}, 1fr)`;
    DOM.gridContainer.innerHTML = ''; // Clear existing cells

    for (let r = 0; r < currentRows; r++) {
        for (let c = 0; c < currentCols; c++) {
            const cellDiv = document.createElement('div');
            
            // Determine state (if gridData exists, use it; otherwise default to unknown)
            let cellState = 'unknown';
            let cellContent = '';

            if (gridData) {
                cellState = gridData[r][c]; // Matches CSS classes: 'safe', 'unknown', 'hazard', 'agent'
            } else if (r === 0 && c === 0) {
                cellState = 'agent'; // Starting position
            }

            // Assign CSS class and text/icon
            cellDiv.className = `cell ${cellState}`;
            
            if (cellState === 'agent') {
                cellContent = '🤖';
            } else if (cellState === 'hazard') {
                cellContent = '☠️'; // Skull for visual flair on found hazards
            }

            cellDiv.innerHTML = cellContent;
            DOM.gridContainer.appendChild(cellDiv);
        }
    }
}

// ==========================================================================
// Event Listeners
// ==========================================================================
DOM.buttons.init.addEventListener('click', initializeEnvironment);
DOM.buttons.reset.addEventListener('click', initializeEnvironment);
DOM.buttons.step.addEventListener('click', takeNextStep);