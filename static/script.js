// Global state
let allPlaces = [];
let filteredPlaces = [];
let selectedIds = new Set();

// Swipe selection state
let isSwipeSelecting = false;
let swipeSelectMode = null; // 'select' or 'deselect'
let lastSwipeIndex = -1;

// DOM elements
const placesList = document.getElementById('placesList');
const searchInput = document.getElementById('searchInput');
const selectAllBtn = document.getElementById('selectAllBtn');
const deselectAllBtn = document.getElementById('deselectAllBtn');
const deleteBtn = document.getElementById('deleteBtn');
const headerCheckbox = document.getElementById('headerCheckbox');
const totalPlacesSpan = document.getElementById('totalPlaces');
const selectedCountSpan = document.getElementById('selectedCount');
const loadingOverlay = document.getElementById('loadingOverlay');
const listContainer = document.getElementById('listContainer');

// Load places on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPlaces();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    searchInput.addEventListener('input', filterPlaces);
    selectAllBtn.addEventListener('click', selectAll);
    deselectAllBtn.addEventListener('click', deselectAll);
    deleteBtn.addEventListener('click', deleteSelected);
    headerCheckbox.addEventListener('change', toggleAllCheckboxes);
    
    // Touch events for swipe selection
    placesList.addEventListener('touchstart', handleTouchStart, { passive: false });
    placesList.addEventListener('touchmove', handleTouchMove, { passive: false });
    placesList.addEventListener('touchend', handleTouchEnd);
    
    // Mouse events for desktop drag selection
    placesList.addEventListener('mousedown', handleMouseDown);
    document.addEventListener('mousemove', handleMouseMove);
    document.addEventListener('mouseup', handleMouseUp);
}

// Load places from API
async function loadPlaces() {
    showLoading(true);
    try {
        const response = await fetch('/api/places');
        allPlaces = await response.json();
        filteredPlaces = [...allPlaces];
        renderPlaces();
        updateStats();
    } catch (error) {
        console.error('Error loading places:', error);
        placesList.innerHTML = '<div class="empty-state"><p>Failed to load places</p></div>';
    } finally {
        showLoading(false);
    }
}

// Filter places based on search
function filterPlaces() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    
    if (!searchTerm) {
        filteredPlaces = [...allPlaces];
    } else {
        filteredPlaces = allPlaces.filter(place => 
            place.name.toLowerCase().includes(searchTerm) ||
            place.id.toString().includes(searchTerm)
        );
    }
    
    renderPlaces();
    updateHeaderCheckbox();
}

// Render places list
function renderPlaces() {
    if (filteredPlaces.length === 0) {
        placesList.innerHTML = '<div class="empty-state"><p>No places found</p></div>';
        return;
    }
    
    placesList.innerHTML = filteredPlaces.map((place, index) => `
        <div class="place-item ${selectedIds.has(place.id) ? 'selected' : ''}" 
             data-id="${place.id}" 
             data-index="${index}">
            <div class="place-checkbox">
                <input type="checkbox" 
                       ${selectedIds.has(place.id) ? 'checked' : ''}>
            </div>
            <div class="place-id">${place.id}</div>
            <div class="place-name">${escapeHtml(place.name)}</div>
        </div>
    `).join('');
    
    // Add click handlers to each item
    document.querySelectorAll('.place-item').forEach(item => {
        item.addEventListener('click', handleItemClick);
    });
}

// Handle item click (toggle selection)
function handleItemClick(e) {
    // Don't toggle if we're in swipe mode
    if (isSwipeSelecting) return;
    
    const item = e.currentTarget;
    const id = parseInt(item.dataset.id);
    
    toggleSelection(id, item);
}

// Toggle single item selection
function toggleSelection(id, element) {
    if (selectedIds.has(id)) {
        selectedIds.delete(id);
        element.classList.remove('selected');
        element.querySelector('input').checked = false;
    } else {
        selectedIds.add(id);
        element.classList.add('selected');
        element.querySelector('input').checked = true;
    }
    updateStats();
    updateHeaderCheckbox();
}

// Set selection state (for swipe)
function setSelection(id, element, shouldSelect) {
    if (shouldSelect && !selectedIds.has(id)) {
        selectedIds.add(id);
        element.classList.add('selected');
        element.querySelector('input').checked = true;
    } else if (!shouldSelect && selectedIds.has(id)) {
        selectedIds.delete(id);
        element.classList.remove('selected');
        element.querySelector('input').checked = false;
    }
}

// =====================
// TOUCH SWIPE SELECTION
// =====================

let touchStartY = 0;
let touchStartElement = null;

function handleTouchStart(e) {
    const item = e.target.closest('.place-item');
    if (!item) return;
    
    touchStartY = e.touches[0].clientY;
    touchStartElement = item;
    
    const id = parseInt(item.dataset.id);
    
    // Determine if we're selecting or deselecting based on initial item state
    swipeSelectMode = selectedIds.has(id) ? 'deselect' : 'select';
    lastSwipeIndex = parseInt(item.dataset.index);
}

function handleTouchMove(e) {
    if (!touchStartElement) return;
    
    const touch = e.touches[0];
    const currentY = touch.clientY;
    const deltaY = Math.abs(currentY - touchStartY);
    
    // Start swipe selection after moving 20px
    if (deltaY > 20 && !isSwipeSelecting) {
        isSwipeSelecting = true;
        // Immediately toggle the starting item
        const id = parseInt(touchStartElement.dataset.id);
        setSelection(id, touchStartElement, swipeSelectMode === 'select');
    }
    
    if (isSwipeSelecting) {
        // Find element under touch point
        const elementUnderTouch = document.elementFromPoint(touch.clientX, touch.clientY);
        const item = elementUnderTouch?.closest('.place-item');
        
        if (item) {
            const currentIndex = parseInt(item.dataset.index);
            const startIndex = parseInt(touchStartElement.dataset.index);
            
            // Select/deselect all items between start and current
            const minIndex = Math.min(startIndex, currentIndex);
            const maxIndex = Math.max(startIndex, currentIndex);
            
            document.querySelectorAll('.place-item').forEach(el => {
                const idx = parseInt(el.dataset.index);
                const id = parseInt(el.dataset.id);
                
                if (idx >= minIndex && idx <= maxIndex) {
                    setSelection(id, el, swipeSelectMode === 'select');
                    el.classList.add('touch-active');
                } else {
                    el.classList.remove('touch-active');
                }
            });
            
            lastSwipeIndex = currentIndex;
        }
        
        // Prevent scrolling while swipe-selecting
        e.preventDefault();
    }
}

function handleTouchEnd() {
    // Remove touch-active class from all
    document.querySelectorAll('.place-item.touch-active').forEach(el => {
        el.classList.remove('touch-active');
    });
    
    if (isSwipeSelecting) {
        updateStats();
        updateHeaderCheckbox();
    }
    
    isSwipeSelecting = false;
    touchStartElement = null;
    swipeSelectMode = null;
    lastSwipeIndex = -1;
}

// =====================
// MOUSE DRAG SELECTION (Desktop)
// =====================

let mouseStartElement = null;

function handleMouseDown(e) {
    const item = e.target.closest('.place-item');
    if (!item) return;
    
    // Only on checkbox or direct item click, not on text selection
    if (e.target.tagName === 'INPUT') return;
    
    mouseStartElement = item;
    const id = parseInt(item.dataset.id);
    swipeSelectMode = selectedIds.has(id) ? 'deselect' : 'select';
    lastSwipeIndex = parseInt(item.dataset.index);
}

function handleMouseMove(e) {
    if (!mouseStartElement) return;
    if (e.buttons !== 1) { // Left mouse button not pressed
        handleMouseUp();
        return;
    }
    
    isSwipeSelecting = true;
    
    const elementUnderMouse = document.elementFromPoint(e.clientX, e.clientY);
    const item = elementUnderMouse?.closest('.place-item');
    
    if (item) {
        const currentIndex = parseInt(item.dataset.index);
        const startIndex = parseInt(mouseStartElement.dataset.index);
        
        const minIndex = Math.min(startIndex, currentIndex);
        const maxIndex = Math.max(startIndex, currentIndex);
        
        document.querySelectorAll('.place-item').forEach(el => {
            const idx = parseInt(el.dataset.index);
            const id = parseInt(el.dataset.id);
            
            if (idx >= minIndex && idx <= maxIndex) {
                setSelection(id, el, swipeSelectMode === 'select');
            }
        });
    }
}

function handleMouseUp() {
    if (isSwipeSelecting) {
        updateStats();
        updateHeaderCheckbox();
    }
    
    isSwipeSelecting = false;
    mouseStartElement = null;
    swipeSelectMode = null;
}

// =====================
// SELECTION CONTROLS
// =====================

function selectAll() {
    filteredPlaces.forEach(place => selectedIds.add(place.id));
    renderPlaces();
    updateStats();
    updateHeaderCheckbox();
}

function deselectAll() {
    selectedIds.clear();
    renderPlaces();
    updateStats();
    updateHeaderCheckbox();
}

function toggleAllCheckboxes() {
    if (headerCheckbox.checked) {
        selectAll();
    } else {
        deselectAll();
    }
}

function updateHeaderCheckbox() {
    const visibleIds = filteredPlaces.map(p => p.id);
    const allVisibleSelected = visibleIds.length > 0 && 
                               visibleIds.every(id => selectedIds.has(id));
    headerCheckbox.checked = allVisibleSelected;
}

// =====================
// DELETE
// =====================

async function deleteSelected() {
    if (selectedIds.size === 0) return;
    
    const count = selectedIds.size;
    const confirmed = confirm(`Delete ${count} place${count > 1 ? 's' : ''}?`);
    if (!confirmed) return;
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/places', {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ids: Array.from(selectedIds) })
        });
        
        const result = await response.json();
        
        if (result.success) {
            selectedIds.clear();
            await loadPlaces();
        } else {
            alert('Delete failed: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting:', error);
        alert('Delete failed. Please try again.');
    } finally {
        showLoading(false);
    }
}

// =====================
// UTILS
// =====================

function updateStats() {
    totalPlacesSpan.textContent = allPlaces.length.toLocaleString();
    selectedCountSpan.textContent = selectedIds.size.toLocaleString();
    deleteBtn.disabled = selectedIds.size === 0;
}

function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
