from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import random

app = Flask(__name__)

# Global variable to store songs data
songs_df = None

def load_songs_data():
    """Load songs data from CSV file"""
    global songs_df
    try:
        # Check if data file exists
        if not os.path.exists('data/songs_500_final.csv'):
            print("❌ ERROR: data/songs_500_final.csv not found!")
            print("💡 Please make sure the CSV file is in the 'data' folder")
            return False
        
        # Load the CSV file
        songs_df = pd.read_csv('data/songs_500_final.csv')
        print(f"✅ Loaded {len(songs_df)} songs successfully!")
        
        # Extract mood from genre
        songs_df['mood'] = songs_df['Genre'].apply(
            lambda x: 'romantic' if 'Romantic' in str(x) else
                     'happy' if 'Happy' in str(x) else
                     'sad' if 'Sad' in str(x) else
                     'energetic' if 'Energetic' in str(x) else 'neutral'
        )
        
        # Rename columns for consistency
        songs_df.rename(columns={
            'Title': 'title',
            'Artist': 'artist', 
            'Language': 'language',
            'Spotify URL': 'spotify_url',
            'Genre': 'genre',
            'Movie/Band Name': 'movie_band'
        }, inplace=True)
        
        return True
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

# Load data when app starts
if load_songs_data():
    print("🎵 Music Recommendation System ready!")
else:
    print("💥 Failed to load data")

@app.route('/')
def index():
    """Main page"""
    if songs_df is None:
        return "Error: Could not load songs data. Please check the console for errors."
    
    moods = ['romantic', 'happy', 'sad', 'energetic']
    languages = songs_df['language'].unique().tolist()
    
    # Get 6 random featured songs
    featured_songs = songs_df.sample(min(6, len(songs_df))).to_dict('records')
    
    # Add index to each song for identification
    for i, song in enumerate(featured_songs):
        song['index'] = i
    
    return render_template('index.html', 
                         moods=moods, 
                         languages=languages,
                         featured_songs=featured_songs)

@app.route('/recommend', methods=['POST'])
def recommend():
    """Get song recommendations based on mood"""
    if songs_df is None:
        return jsonify({'success': False, 'error': 'Data not loaded'})
    
    try:
        data = request.get_json()
        mood = data.get('mood')
        language = data.get('language', 'all')
        
        if not mood:
            return jsonify({'success': False, 'error': 'No mood specified'})
        
        # Filter songs by mood
        mood_songs = songs_df[songs_df['mood'] == mood]
        
        # Further filter by language if specified
        if language != 'all':
            mood_songs = mood_songs[mood_songs['language'] == language]
        
        # Get random recommendations
        if len(mood_songs) > 0:
            recommendations = mood_songs.sample(min(10, len(mood_songs))).to_dict('records')
            
            # Add index to each song
            for i, song in enumerate(recommendations):
                song['index'] = i
        else:
            recommendations = []
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/search')
def search_songs():
    """Search for songs by title, artist, or movie/band"""
    if songs_df is None:
        return jsonify({'songs': []})
    
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify({'songs': []})
    
    # Search in title, artist, and movie/band name
    filtered_songs = songs_df[
        songs_df['title'].str.lower().str.contains(query, na=False) |
        songs_df['artist'].str.lower().str.contains(query, na=False) |
        songs_df['movie_band'].str.lower().str.contains(query, na=False)
    ]
    
    results = filtered_songs.head(10).to_dict('records')
    
    # Add index to each song
    for i, song in enumerate(results):
        song['index'] = i
    
    return jsonify({'songs': results})

@app.route('/health')
def health_check():
    """Health check endpoint"""
    if songs_df is not None:
        return jsonify({
            'status': 'healthy',
            'songs_loaded': len(songs_df),
            'moods': songs_df['mood'].value_counts().to_dict()
        })
    else:
        return jsonify({'status': 'error', 'message': 'Data not loaded'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)