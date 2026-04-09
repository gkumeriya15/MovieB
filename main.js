// Simple MovieBox Frontend
// This code calls the API and shows results

const API_URL = 'https://movieb-rsoz.onrender.com/api/v1/search';

document.getElementById('search-button').addEventListener('click', searchMovies);

async function searchMovies() {
    const query = document.getElementById('search-input').value.trim();
    if (!query) {
        alert('Please enter a search term');
        return;
    }

    // Show loading
    document.getElementById('results').innerHTML = '<p>Loading...</p>';

    try {
        // Call the API
        const response = await fetch(`${API_URL}?q=${encodeURIComponent(query)}&type=ALL&page=1&per_page=24`);
        const data = await response.json();

        // Check if successful
        if (data.success && data.data && data.data.length > 0) {
            displayResults(data.data);
        } else {
            document.getElementById('results').innerHTML = '<p>No results found</p>';
        }
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('results').innerHTML = '<p>Error loading results. Please try again.</p>';
    }
}

function displayResults(movies) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';

    movies.forEach(movie => {
        const movieDiv = document.createElement('div');
        movieDiv.className = 'movie-card';

        const imageUrl = movie.poster || 'https://via.placeholder.com/200x300?text=No+Image';
        const title = movie.title || 'Unknown Title';

        movieDiv.innerHTML = `
            <img src="${imageUrl}" alt="${title}" onerror="this.src='https://via.placeholder.com/200x300?text=No+Image'">
            <h3>${title}</h3>
        `;

        resultsDiv.appendChild(movieDiv);
    });
}