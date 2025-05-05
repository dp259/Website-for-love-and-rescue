function clearSessionAndGoBack() {
    fetch('/clear_dog_session')
    .then(response => {
        if (response.ok) {
            window.location.href = '/adopt';
        } else {
            console.error('Failed to clear session.');
        }
    })
    .catch(error => console.error('Error:', error));
}

function toggleDropdown(dropdownId) {
    var dropdown = document.getElementById(dropdownId);
    const isVisible = dropdown.style.display === "block";
    closeAllDropdowns();
    dropdown.style.display = isVisible ? "none" : "block";
}

function closeAllDropdowns() {
    const dropdowns = document.querySelectorAll('.dropdown-filter');
    dropdowns.forEach(dropdown => {
        dropdown.style.display = "none";
    });
}

// Close dropdown if clicking outside
document.addEventListener('click', function (event) {
    const filterContainers = document.querySelectorAll('.filter-container');
    let clickedInside = false;

    // Check if click was inside any dropdown
    filterContainers.forEach(container => {
        if (container.contains(event.target)) {
            clickedInside = true;
        }
    });

    if (!clickedInside) {
        closeAllDropdowns();
    }
});

function applyFilters() {
    const name = document.getElementById('name').value;
    const sex = Array.from(document.getElementById('sex').selectedOptions).map(option => option.value);
    const breed = Array.from(document.getElementById('breed').selectedOptions).map(option => option.value);
    const characteristics = Array.from(document.getElementById('characteristics').selectedOptions).map(option => option.value);
    const age = Array.from(document.getElementById('age').selectedOptions).map(option => option.value)

    const filters = {
        name,
        sex,
        breed,
        characteristics,
        age,
    };

    fetch('/filter_dogs', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(filters),
    })
    .then(response => response.json())
    .then(data => updateDogGrid(data))
    .catch(error => console.error('Error:', error));
}

function updateDogGrid(dogs) {
    const dogGrid = document.querySelector('.dog-grid');
    dogGrid.innerHTML = ''; // Clear the current grid

    if (dogs.length === 0) {
        dogGrid.innerHTML = '<p>No dogs available for adoption at this time.</p>';
        return;
    }

    dogs.forEach(dog => {
        const dogItem = document.createElement('div');
        dogItem.className = 'dog-item';
        dogItem.innerHTML = `
            <form action="/dog_details/${dog.dog_id}" method="GET">
                <button type="submit" class="dog-button">
                    <img src="/static/images/dog.jpg" alt="Image of ${dog.name}">
                </button>
                <p><strong>${dog.name}</strong></p>
            </form>
        `;
        dogGrid.appendChild(dogItem);
    });
}

function redirect(url) {
    window.location.href = `{{ url_for('home') }}`.replace('home', url);
}

function resetFilters() {
    document.getElementById('name').value = '';

    ['sex', 'breed', 'characteristics', 'age'].forEach(id => {
        const select = document.getElementById(id);
        Array.from(select.options).forEach(option => {
            option.selected = false; // Deselect all options
        });
    });

    applyFilters();
}