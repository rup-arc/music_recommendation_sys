class MusicRecommender {
    constructor() {
        this.currentMood = null;
        this.currentLanguage = 'all';
        this.initEventListeners();
    }

    initEventListeners() {
        // Mood selection
        document.querySelectorAll('.mood-card').forEach(card => {
            card.addEventListener('click', (e) => {
                this.selectMood(e.currentTarget.dataset.mood);
            });
        });

        // Language filter
        document.getElementById('language-filter').addEventListener('change', (e) => {
            this.currentLanguage = e.target.value;
            if (this.currentMood) {
                this.getRecommendationsByMood(this.currentMood);
            }
        });

        // Search functionality
        document.getElementById('search-btn').addEventListener('click', () => {
            this.searchSongs();
        });

        document.getElementById('search-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.searchSongs();
            }
        });

        // Featured songs click
        document.querySelectorAll('.song-card').forEach(card => {
            card.addEventListener('click', (e) => {
                const songIndex = e.currentTarget.dataset.songIndex;
                this.playSong(songIndex);
            });
        });
    }

    selectMood(mood) {
        this.currentMood = mood;
        
        // Update UI
        document.querySelectorAll('.mood-card').forEach(card => {
            card.classList.remove('active');
        });
        document.querySelector(`.mood-card[data-mood="${mood}"]`).classList.add('active');
        
        this.getRecommendationsByMood(mood);
    }

    async getRecommendationsByMood(mood) {
        this.showLoading();
        
        try {
            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mood: mood,
                    language: this.currentLanguage
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displayRecommendations(data.recommendations, `Songs for ${mood} mood`);
            } else {
                this.showError('Failed to get recommendations: ' + data.error);
            }
        } catch (error) {
            console.error('Error:', error);
            this.showError('Failed to connect to server. Make sure the server is running.');
        }
    }

    async searchSongs() {
        const query = document.getElementById('search-input').value.trim();
        
        if (!query) {
            document.getElementById('search-results').innerHTML = '';
            return;
        }
        
        try {
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
            const data = await response.json();
            
            this.displaySearchResults(data.songs);
        } catch (error) {
            console.error('Error:', error);
            this.showError('Search failed');
        }
    }

    displaySearchResults(songs) {
        const container = document.getElementById('search-results');
        
        if (songs.length === 0) {
            container.innerHTML = '<p class="text-muted">No songs found</p>';
            return;
        }
        
        container.innerHTML = songs.map(song => `
            <div class="search-result" onclick="recommender.playSong(${song.index})">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="mb-1">${song.title}</h6>
                        <small class="text-muted">${song.artist} • ${song.language}</small>
                    </div>
                    <span class="badge" data-mood="${song.mood}">${song.mood}</span>
                </div>
            </div>
        `).join('');
    }

    displayRecommendations(songs, title = 'Recommended Songs') {
        const container = document.getElementById('recommendations-container');
        
        if (songs.length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <p class="text-muted">No recommendations found. Try a different mood or language.</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = `
            <h5 class="mb-3">${title} (${songs.length} songs)</h5>
            <div class="row">
                ${songs.map(song => `
                    <div class="col-md-6 mb-3">
                        <div class="song-card" onclick="recommender.playSong(${song.index})">
                            <div class="d-flex justify-content-between align-items-start">
                                <div class="flex-grow-1">
                                    <h6 class="mb-1">${song.title}</h6>
                                    <p class="mb-1 text-muted small">${song.artist}</p>
                                    <p class="mb-0 text-muted small">${song.language} • ${song.movie_band}</p>
                                </div>
                                <span class="badge ms-2" data-mood="${song.mood}">${song.mood}</span>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    playSong(songIndex) {
        alert(`Playing song with index: ${songIndex}\n\nIn a full implementation, this would play the song using the Spotify URL.`);
        
        // In a real implementation, you would:
        // 1. Fetch song details using songIndex
        // 2. Extract the Spotify URL
        // 3. Embed the Spotify player or redirect to Spotify
    }

    showLoading() {
        const container = document.getElementById('recommendations-container');
        container.innerHTML = `
            <div class="loading">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Finding perfect recommendations...</p>
            </div>
        `;
    }

    showError(message) {
        const container = document.getElementById('recommendations-container');
        container.innerHTML = `
            <div class="alert alert-danger" role="alert">
                <i class="fas fa-exclamation-triangle me-2"></i>
                ${message}
            </div>
        `;
    }
}

// Initialize the application when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.recommender = new MusicRecommender();
});