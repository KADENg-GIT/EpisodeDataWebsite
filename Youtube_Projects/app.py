from flask import Flask, render_template
import requests
from datetime import datetime
import os

from dotenv import load_dotenv
load_dotenv()

print(f"Environment variables: {os.environ}")
print(f"TMDB_API_KEY from os.environ: {os.environ.get('TMDB_API_KEY')}")


app = Flask(__name__)

def get_airing_today_shows(api_key):
    """
    Fetches TV shows airing today from TMDb API.
    """
    url = 'https://api.themoviedb.org/3/tv/airing_today'
    params = {
        'api_key': api_key,
        'language': 'en-US',
        'page': 1,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        shows = response.json().get('results', [])
        return shows
    else:
        print(f"Error fetching data: {response.status_code}")
        return []

def get_episode_details(api_key, show_id):
    """
    Fetches episode details for the show's latest aired or next episode.
    """
    url = f'https://api.themoviedb.org/3/tv/{show_id}'
    params = {
        'api_key': api_key,
        'language': 'en-US',
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        show_details = response.json()
        today = datetime.now().date()
        next_episode = show_details.get('next_episode_to_air')
        last_episode = show_details.get('last_episode_to_air')

        if next_episode and datetime.strptime(next_episode['air_date'], '%Y-%m-%d').date() == today:
            return next_episode
        elif last_episode and datetime.strptime(last_episode['air_date'], '%Y-%m-%d').date() == today:
            return last_episode
        else:
            return None
    else:
        print(f"Error fetching data for show ID {show_id}: {response.status_code}")
        return None

def display_trending_episodes(api_key, shows):
    """
    Returns a ranked list of episodes airing today.
    """
    episodes = []
    for show in shows:
        show_id = show.get('id')
        popularity = show.get('popularity', 0)
        episode = get_episode_details(api_key, show_id)
        if episode:
            episodes.append({
                'show_name': show.get('name'),
                'popularity': popularity,
                'episode': episode
            })

    # Sort episodes based on the popularity of their shows
    episodes.sort(key=lambda x: x['popularity'], reverse=True)

    return episodes

@app.route('/')
def home():
    # Get the API key from environment variables
    api_key = os.environ.get('TMDB_API_KEY')
    if not api_key:
        return "Error: TMDB API key is not set."

    # Fetch TV shows airing today
    shows = get_airing_today_shows(api_key)
    episodes = display_trending_episodes(api_key, shows)

    return render_template('home.html', episodes=episodes)

if __name__ == '__main__':
    app.run(debug=True)