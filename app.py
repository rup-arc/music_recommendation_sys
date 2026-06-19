from flask import Flask, render_template, request, jsonify
import pandas as pd
import os
import random
import logging
import boto3
from watchtower import CloudWatchLogHandler
from pythonjsonlogger import jsonlogger

app = Flask(__name__)

# S3 Configuration
S3_BUCKET = os.getenv('S3_BUCKET', 'music-recommendation-data-production')
S3_KEY = os.getenv('S3_KEY', 'songs_500_spotify.csv')
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')

# CloudWatch Logging Setup
def setup_logging():
    """Configure CloudWatch logging for the application"""
    log_group = os.getenv('LOG_GROUP', '/ecs/music-recommendation')
    log_stream = os.getenv('LOG_STREAM', 'music-app-stream')
    aws_region = os.getenv('AWS_REGION', 'us-east-1')
    
    # Console handler (for local debugging)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # JSON formatter for structured logging
    formatter = jsonlogger.JsonFormatter('%(timestamp)s %(level)s %(name)s %(message)s')
    console_handler.setFormatter(formatter)
    
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.INFO)
    
    # CloudWatch handler (for AWS logging)
    try:
        # Set AWS region for boto3
        import boto3
        boto3.setup_default_session(region_name=aws_region)

        cloudwatch_handler = CloudWatchLogHandler(
            log_group=log_group,
            stream_name=log_stream
        )
        cloudwatch_handler.setFormatter(formatter)
        app.logger.addHandler(cloudwatch_handler)
        app.logger.info("CloudWatch logging initialized", extra={'log_group': log_group})
    except Exception as e:
        app.logger.warning(f"CloudWatch logging not available: {e}")

setup_logging()

# Global variable to store songs data
songs_df = None

def load_songs_data():
    """Load songs data from S3 or local CSV file"""
    global songs_df
    try:
        # Try to load from S3 first
        try:
            s3_client = boto3.client('s3', region_name=AWS_REGION)
            obj = s3_client.get_object(Bucket=S3_BUCKET, Key=S3_KEY)
            songs_df = pd.read_csv(obj['Body'])
            app.logger.info(f"Loaded {len(songs_df)} songs from S3 bucket {S3_BUCKET}", extra={'source': 's3', 'bucket': S3_BUCKET, 'count': len(songs_df)})
        except Exception as e:
            app.logger.warning(f"Failed to load from S3: {e}, falling back to local file", extra={'error': str(e)})
            # Fallback to local file
            if not os.path.exists('data/songs_500_spotify.csv'):
                app.logger.error("Data file not found in S3 or locally", extra={'s3_bucket': S3_BUCKET, 'local_file': 'data/songs_500_spotify.csv'})
                return False
            
            songs_df = pd.read_csv('data/songs_500_spotify.csv')
            app.logger.info(f"Loaded {len(songs_df)} songs from local file", extra={'source': 'local', 'count': len(songs_df)})
        
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
        app.logger.error(f"Error loading data: {e}", extra={'error': str(e)})
        return False

# Load data when app starts
if load_songs_data():
    app.logger.info("Music Recommendation System ready")
else:
    app.logger.error("Failed to load data")

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
        app.logger.error("Recommendation request failed: data not loaded")
        return jsonify({'success': False, 'error': 'Data not loaded'})
    
    try:
        data = request.get_json()
        mood = data.get('mood')
        language = data.get('language', 'all')
        
        app.logger.info(f"Recommendation request", extra={'mood': mood, 'language': language})
        
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
            
            app.logger.info(f"Returned {len(recommendations)} recommendations", extra={'count': len(recommendations)})
        else:
            recommendations = []
            app.logger.warning(f"No songs found for mood: {mood}")
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'count': len(recommendations)
        })
        
    except Exception as e:
        app.logger.error(f"Recommendation error: {e}", extra={'error': str(e)})
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
        return jsonify({
            'status': 'error',
            'message': 'Data not loaded'
        }), 503

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
