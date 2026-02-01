// Global state
let allPlaces = [];
let filteredPlaces = [];
let selectedIds = new Set();

// DOM elements
const placesList = document.getElementById('placesList');
const searchInput = document.getElementById('searchInput');
const typeFilter = document.getElementById('typeFilter');
const deleteBtn = document.getElementById('deleteBtn');
const headerCheckbox = document.getElementById('headerCheckbox');
const totalPlacesSpan = document.getElementById('totalPlaces');
const selectedCountSpan = document.getElementById('selectedCount');
const loadingOverlay = document.getElementById('loadingOverlay');

// Load places on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPlaces();
    setupEventListeners();
});

// Setup event listeners
function setupEventListeners() {
    searchInput.addEventListener('input', filterPlaces);
    typeFilter.addEventListener('change', filterPlaces);
    deleteBtn.addEventListener('click', deleteSelected);
    headerCheckbox.addEventListener('change', toggleAllCheckboxes);
}

// Load places from API
async function loadPlaces() {
    showLoading(true);
    try {
        const response = await fetch('/api/places');
        allPlaces = await response.json();
        filteredPlaces = [...allPlaces];
        
        populateTypeFilter();
        renderPlaces();
        updateStats();
    } catch (error) {
        console.error('Error loading places:', error);
        placesList.innerHTML = '<div class="empty-state"><p>Failed to load places</p></div>';
    } finally {
        showLoading(false);
    }
}

// Populate type filter dropdown
function populateTypeFilter() {
    const types = new Set();
    allPlaces.forEach(place => {
        if (place.types) {
            place.types.forEach(type => types.add(type));
        }
    });
    
    const sortedTypes = Array.from(types).sort();
    
    typeFilter.innerHTML = '<option value="">All Types</option>';
    sortedTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type.replace(/_/g, ' ');
        typeFilter.appendChild(option);
    });
}

// Filter places based on search and type
function filterPlaces() {
    const searchTerm = searchInput.value.toLowerCase().trim();
    const selectedType = typeFilter.value;
    
    filteredPlaces = allPlaces.filter(place => {
        // Search filter
        const matchesSearch = !searchTerm || 
            place.name.toLowerCase().includes(searchTerm) ||
            place.id.toString().includes(searchTerm);
        
        // Type filter
        const matchesType = !selectedType || 
            (place.types && place.types.includes(selectedType));
        
        return matchesSearch && matchesType;
    });
    
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
                       ${selectedIds.has(place.id) ? 'checked' : ''}
                       onchange="handleCheckboxChange(event, ${place.id})">
            </div>
            <div class="place-id">${place.id}</div>
            <div class="place-name">${escapeHtml(place.name)}</div>
        </div>
    `).join('');
}

// Handle checkbox change - ONLY way to select/deselect
function handleCheckboxChange(event, id) {
    event.stopPropagation();
    
    const item = event.target.closest('.place-item');
    
    if (event.target.checked) {
        selectedIds.add(id);
        item.classList.add('selected');
    } else {
        selectedIds.delete(id);
        item.classList.remove('selected');
    }
    
    updateStats();
    updateHeaderCheckbox();
}

// Toggle all checkboxes (header checkbox)
function toggleAllCheckboxes() {
    if (headerCheckbox.checked) {
        // Select all visible
        filteredPlaces.forEach(place => selectedIds.add(place.id));
    } else {
        // Deselect all visible
        filteredPlaces.forEach(place => selectedIds.delete(place.id));
    }
    
    renderPlaces();
    updateStats();
}

// Update header checkbox state
function updateHeaderCheckbox() {
    const visibleIds = filteredPlaces.map(p => p.id);
    const allVisibleSelected = visibleIds.length > 0 && 
                               visibleIds.every(id => selectedIds.has(id));
    headerCheckbox.checked = allVisibleSelected;
}

// Delete selected places
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

// Update statistics
function updateStats() {
    totalPlacesSpan.textContent = allPlaces.length.toLocaleString();
    selectedCountSpan.textContent = selectedIds.size.toLocaleString();
    deleteBtn.disabled = selectedIds.size === 0;
}

// Show/hide loading overlay
function showLoading(show) {
    loadingOverlay.style.display = show ? 'flex' : 'none';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
