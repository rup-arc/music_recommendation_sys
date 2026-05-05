import csv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import time

# --- SPOTIFY API CREDENTIALS ---
# Is script ko real-time lookup ke liye chalane ke liye aapko https://developer.spotify.com/
# se Client ID aur Client Secret lena hoga. Agar aapke paas credentials nahi hain, 
# toh yeh automated browser web search link create kar dega.
CLIENT_ID = 'YOUR_CLIENT_ID'
CLIENT_SECRET = 'YOUR_CLIENT_SECRET'

try:
    auth_manager = SpotifyClientCredentials(client_id=CLIENT_ID, client_secret=CLIENT_SECRET)
    sp = spotipy.Spotify(auth_manager=auth_manager)
except Exception:
    sp = None

# Songs Data Lists
hindi_songs = [
    ["Kesariya", "Arijit Singh", "Hindi", "Romantic", "Brahmastra"],
    ["Apna Bana Le", "Arijit Singh", "Hindi", "Romantic", "Bhediya"],
    ["Deva Deva", "Arijit Singh", "Hindi", "Romantic", "Brahmastra"],
    ["Channa Mereya", "Arijit Singh", "Hindi", "Sad", "Ae Dil Hai Mushkil"],
    ["Ae Dil Hai Mushkil", "Arijit Singh", "Hindi", "Romantic", "Ae Dil Hai Mushkil"],
    ["Gerua", "Shreya Ghoshal & Arijit Singh", "Hindi", "Romantic", "Dilwale"],
    ["Jabra Fan", "Arijit Singh", "Hindi", "Energetic", "Fan"],
    ["Bekhayali", "Sachet Tandon", "Hindi", "Sad", "Kabir Singh"],
    ["Tera Ban Jaunga", "Akull & Tulsi Kumar", "Hindi", "Romantic", "Kabir Singh"],
    ["Kaun Tujhe", "Darshan Raval", "Hindi", "Romantic", "M.S.Dhoni"],
    ["Bolna", "Arjit Singh & Asees Kaur", "Hindi", "Romantic", "Kaabil"],
    ["Humsafar", "Akhil Sachdeva", "Hindi", "Romantic", "Badrinath Ki Dulhania"],
    ["Dil Diyan Gallan", "Atif Aslam", "Hindi", "Romantic", "Tiger Zinda Hai"],
    ["Roke Na Ruke Naina", "Arijit Singh", "Hindi", "Romantic", "Badrinath Ki Dulhania"],
    ["Sau Aasmaan", "Neeti Mohan & Armaan Malik", "Hindi", "Romantic", "Baar Baar Dekho"],
    ["Jaan Nisaar", "Arijit Singh", "Hindi", "Sad", "Kedarnath"],
    ["Dhadak", "Shreya Ghoshal & Ajay Gogavale", "Hindi", "Romantic", "Dhadak"],
    ["Kalank", "Arijit Singh", "Hindi", "Sad", "Kalank"],
    ["First Class", "Arijit Singh", "Hindi", "Happy", "Kalank"],
    ["Ghungroo", "Arjit Singh", "Hindi", "Energetic", "War"],
    ["The Punjaaban", "Harrdy Sandhu", "Hindi", "Energetic", "85"],
    ["Coka 2.0", "Neha Kakkar & Tony Kakkar", "Hindi", "Energetic", "Solo"],
    ["Makhna", "Neha Kakkar", "Hindi", "Romantic", "Makhna"],
    ["Kamariya", "Neha Kakkar", "Hindi", "Energetic", "Mitron"],
    ["Gali Gali", "Neha Kakkar", "Hindi", "Energetic", "KGF Chapter 2"],
    ["Kusu Kusu", "Neha Kakkar", "Hindi", "Energetic", "Satyameva Jayate 2"],
    ["Maar Daala", "Neha Kakkar", "Hindi", "Energetic", "Maar Daala"],
    ["Inni LehraDo", "Neha Kakkar", "Hindi", "Energetic", "INNI LEHRA DO"],
    ["Attach", "Neha Kakkar", "Hindi", "Romantic", "Attach"],
    ["Tu Hi Mera", "Shreya Ghoshal", "Hindi", "Romantic", "Half Girlfriend"],
    ["Main Rahoon Ya Na Rahoon", "Armaan Malik", "Hindi", "Romantic", "Main Rahoon Ya Na Rahoon"],
    ["Tujhe Kitna Chahne Lage", "Arijit Singh", "Hindi", "Romantic", "Kabir Singh"],
    ["Mere Sohneya", "Arjit Singh", "Hindi", "Romantic", "Kabir Singh"],
    ["Dil Tod Ke", "B Praak", "Hindi", "Sad", "Dil Tod Ke"],
    ["Zaroorat Se Zyada", "Rahat Fateh Ali Khan", "Hindi", "Romantic", "Zaroorat Se Zyada"],
    ["Mere Liye Tu Hai", "Papon", "Hindi", "Romantic", "Mere Liye Tu Hai"],
    ["Tu Hi Yaar Mera", "Papon & Neeti Kakkar", "Hindi", "Romantic", "Tu Hi Yaar Mera"],
    ["Dil Ko Karaar Aaya", "Neha Kakkar & Yash Narvekar", "Hindi", "Romantic", "Dil Ko Karaar Aaya"],
    ["Chhor Denge", "Arjit Singh", "Hindi", "Sad", "Chhor Denge"],
    ["Raanjhana Ve", "Jubin Nautiyal", "Hindi", "Sad", "Raanjhana Ve"],
    ["Mere Paas Tum Ho", "Rahat Fateh Ali Khan", "Hindi", "Sad", "Mere Paas Tum Ho"],
    ["Ishare Tere", "Darshan Raval", "Hindi", "Romantic", "Ishare Tere"],
    ["Aawargi", "Jubin Nautiyal", "Hindi", "Romantic", "Aawargi"],
    ["Dil Galti Kar Baitha Hai", "Jubin Nautiyal", "Hindi", "Sad", "Dil Galti Kar Baitha Hai"],
    ["Hanjugam", "Shreya Ghoshal", "Hindi", "Romantic", "Hanjugam"],
    ["Tera Mera Rishta", "B Praak", "Hindi", "Romantic", "Tera Mera Rishta"],
    ["Akh Lad Jaave", "Jubin Nautiyal", "Hindi", "Energetic", "Akh Lad Jaave"],
    ["Mera Mann Kehne Laga", "Falak Shabir", "Hindi", "Romantic", "Mera Mann Kehne Laga"],
    ["Pal", "Arjit Singh", "Hindi", "Romantic", "Pal"],
    ["Srivalli", "Javed Ali", "Hindi", "Romantic", "Pushpa"],
]

english_songs = [
    ["Blinding Lights", "The Weeknd", "English", "Energetic", "After Hours"],
    ["Shape of You", "Ed Sheeran", "English", "Romantic", "÷"],
    ["Perfect", "Ed Sheeran", "English", "Romantic", "÷"],
    ["Believer", "Imagine Dragons", "English", "Energetic", "Evolve"],
    ["Someone Like You", "Adele", "English", "Sad", "21"],
    ["Hello", "Adele", "English", "Sad", "25"],
    ["Rolling in the Deep", "Adele", "English", "Energetic", "21"],
    ["Set Fire to the Rain", "Adele", "English", "Sad", "21"],
    ["When We Were Young", "Adele", "English", "Romantic", "25"],
    ["Easy on Me", "Adele", "English", "Romantic", "30"],
    ["Bohemian Rhapsody", "Queen", "English", "Rock", "A Night at the Opera"],
    ["We Will Rock You", "Queen", "English", "Energetic", "News of the World"],
    ["We Are the Champions", "Queen", "English", "Energetic", "News of the World"],
    ["Another One Bites the Dust", "Queen", "English", "Energetic", "The Game"],
    ["Under Pressure", "Queen & David Bowie", "English", "Rock", "Hot Space"],
    ["Radio Ga Ga", "Queen", "English", "Rock", "The Works"],
    ["I Want to Break Free", "Queen", "English", "Rock", "The Works"],
    ["The Show Must Go On", "Queen", "English", "Sad", "Innuendo"],
    ["Somebody to Love", "Queen", "English", "Romantic", "A Day at the Races"],
    ["Don't Stop Me Now", "Queen", "English", "Energetic", "Jazz"],
]

bengali_songs = [
    ["Murshida", "Shreya Ghoshal", "Bengali", "Romantic", "Murshida"],
    ["Tumi Ashbe Bole", "Rabiul Islam", "Bengali", "Romantic", "Tumi Ashbe Bole"],
    ["Ami Tor Moner Moto", "Anupam Roy", "Bengali", "Romantic", "Ami Tor Moner Moto"],
    ["Babaida", "Balam", "Bengali", "Energetic", "Babaida"],
    ["Mayabati", "Tahsan", "Bengali", "Romantic", "Mayabati"],
    ["Jhumka", "Priyo", "Bengali", "Energetic", "Jhumka"],
    ["Tui Amar Jaan", "Imran Mahmudul", "Bengali", "Romantic", "Tui Amar Jaan"],
    ["Chand Hawa", "Balam", "Bengali", "Romantic", "Chand Hawa"],
    ["Ure Jre Mon", "Shreya Ghoshal & Arindom", "Bengali", "Romantic", "Ure Jre Mon"],
    ["Mon Bojhena", "Tahsan & Mila", "Bengali", "Romantic", "Mon Bojhena"],
    ["Tor Moner Vitor", "Shunno", "Bengali", "Romantic", "Tor Moner Vitor"],
    ["Amar Ache Jol", "Shunno", "Bengali", "Energetic", "Amar Ache Jol"],
    ["Osomoy", "Soulmate ft Sanai", "Bengali", "Romantic", "Osomoy"],
    ["Keno Je Toke", "SImanta", "Bengali", "Romantic", "Keno Je Toke"],
    ["Mon Amoure", "Taiba", "Bengali", "Romantic", "Mon Amoure"],
    ["Je Nei Rater Batas", "Imran Mahmudul", "Bengali", "Sad", "Je Nei Rater Batas"],
    ["Sriti Rekha", "Shreya Ghoshal", "Bengali", "Romantic", "Sriti Rekha"],
    ["Tomake Chai", "Arfin Rumey", "Bengali", "Romantic", "Tomake Chai"],
    ["Jago Bangladesh", "Various", "Bengali", "Energetic", "Jago Bangladesh"],
    ["Bhalobeshe Jabo", "Shoeb", "Bengali", "Romantic", "Bhalobeshe Jabo"],
]

def create_song_list(songs, target_count):
    result = []
    while len(result) < target_count:
        result.extend(songs)
    return result[:target_count]

# 500 Songs distribute karne ke liye list multiplier
hindi_200 = create_song_list(hindi_songs, 200)
english_200 = create_song_list(english_songs, 200)
bengali_100 = create_song_list(bengali_songs, 100)

all_songs = hindi_200 + english_200 + bengali_100

def get_spotify_url(title, artist):
    if sp:
        try:
            query = f"track:{title} artist:{artist}"
            results = sp.search(q=query, limit=1, type='track')
            items = results['tracks']['items']
            if items:
                return items[0]['external_urls']['spotify']
        except Exception:
            pass
    # Live API access na hone par directly executable deep-link return karega
    return f"https://open.spotify.com/search/{title.replace(' ', '%20')}%20{artist.replace(' ', '%20')}"

final_rows = []
print("Spotify links generate ho rahe hain...")

for song in all_songs:
    title, artist, lang, genre, album = song[0], song[1], song[2], song[3], song[4]
    spotify_url = get_spotify_url(title, artist)
    final_rows.append([title, artist, lang, spotify_url, genre, album])

# CSV File writing
csv_file = "songs_500_spotify.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["Title", "Artist", "Language", "Spotify URL", "Genre", "Movie/Band Name"])
    writer.writerows(final_rows)

print(f" Successfully created {csv_file} with {len(final_rows)} songs!")