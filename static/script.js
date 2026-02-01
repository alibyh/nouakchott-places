// Global state
let allPlaces = [];
let filteredPlaces = [];
let selectedIds = new Set();

// DOM elements
const placesTableBody = document.getElementById('placesTableBody');
const searchInput = document.getElementById('searchInput');
const typeFilter = document.getElementById('typeFilter');
const selectAllBtn = document.getElementById('selectAllBtn');
const deselectAllBtn = document.getElementById('deselectAllBtn');
const deleteBtn = document.getElementById('deleteBtn');
const headerCheckbox = document.getElementById('headerCheckbox');
const totalPlacesSpan = document.getElementById('totalPlaces');
const selectedCountSpan = document.getElementById('selectedCount');
const loadingOverlay = document.getElementById('loadingOverlay');

// Load places on page load
document.addEventListener('DOMContentLoaded', () => {
    loadPlaces();
});

// Event listeners
searchInput.addEventListener('input', filterPlaces);
typeFilter.addEventListener('change', filterPlaces);
selectAllBtn.addEventListener('click', selectAll);
deselectAllBtn.addEventListener('click', deselectAll);
deleteBtn.addEventListener('click', deleteSelected);
headerCheckbox.addEventListener('change', toggleAllCheckboxes);

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
        alert('Failed to load places. Please refresh the page.');
    } finally {
        showLoading(false);
    }
}

// Populate type filter dropdown
function populateTypeFilter() {
    const types = new Set();
    allPlaces.forEach(place => {
        place.types.forEach(type => types.add(type));
    });
    
    const sortedTypes = Array.from(types).sort();
    
    typeFilter.innerHTML = '<option value="">All Types</option>';
    sortedTypes.forEach(type => {
        const option = document.createElement('option');
        option.value = type;
        option.textContent = type;
        typeFilter.appendChild(option);
    });
}

// Filter places based on search and type
function filterPlaces() {
    const searchTerm = searchInput.value.toLowerCase();
    const selectedType = typeFilter.value;
    
    filteredPlaces = allPlaces.filter(place => {
        const matchesSearch = place.name.toLowerCase().includes(searchTerm) ||
                             place.types.some(type => type.toLowerCase().includes(searchTerm));
        
        const matchesType = !selectedType || place.types.includes(selectedType);
        
        return matchesSearch && matchesType;
    });
    
    renderPlaces();
    updateHeaderCheckbox();
}

// Render places table
function renderPlaces() {
    placesTableBody.innerHTML = '';
    
    if (filteredPlaces.length === 0) {
        placesTableBody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; padding: 40px; color: #6c757d;">
                    No places found
                </td>
            </tr>
        `;
        return;
    }
    
    filteredPlaces.forEach(place => {
        const row = document.createElement('tr');
        if (selectedIds.has(place.id)) {
            row.classList.add('selected');
        }
        
        row.innerHTML = `
            <td>
                <input type="checkbox" 
                       class="place-checkbox" 
                       data-id="${place.id}"
                       ${selectedIds.has(place.id) ? 'checked' : ''}>
            </td>
            <td class="place-id">${place.id}</td>
            <td class="place-name">${escapeHtml(place.name)}</td>
            <td>
                <div class="place-types">
                    ${place.types.map(type => `<span class="type-badge">${type}</span>`).join('')}
                </div>
            </td>
            <td class="place-location">${place.latitude.toFixed(6)}, ${place.longitude.toFixed(6)}</td>
        `;
        
        // Add checkbox event listener
        const checkbox = row.querySelector('.place-checkbox');
        checkbox.addEventListener('change', (e) => {
            const id = parseInt(e.target.dataset.id);
            if (e.target.checked) {
                selectedIds.add(id);
                row.classList.add('selected');
            } else {
                selectedIds.delete(id);
                row.classList.remove('selected');
            }
            updateStats();
            updateHeaderCheckbox();
        });
        
        placesTableBody.appendChild(row);
    });
}

// Select all visible places
function selectAll() {
    filteredPlaces.forEach(place => selectedIds.add(place.id));
    renderPlaces();
    updateStats();
    updateHeaderCheckbox();
}

// Deselect all places
function deselectAll() {
    selectedIds.clear();
    renderPlaces();
    updateStats();
    updateHeaderCheckbox();
}

// Toggle all checkboxes
function toggleAllCheckboxes() {
    if (headerCheckbox.checked) {
        selectAll();
    } else {
        deselectAll();
    }
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
    
    const confirmed = confirm(`Are you sure you want to delete ${selectedIds.size} place(s)?\n\nThis action cannot be undone.`);
    if (!confirmed) return;
    
    showLoading(true);
    
    try {
        const response = await fetch('/api/places', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                ids: Array.from(selectedIds)
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            alert(`Successfully deleted ${result.deleted_count} place(s).\n${result.remaining_count} places remaining.`);
            selectedIds.clear();
            await loadPlaces();
        } else {
            alert('Failed to delete places: ' + (result.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error deleting places:', error);
        alert('Failed to delete places. Please try again.');
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
