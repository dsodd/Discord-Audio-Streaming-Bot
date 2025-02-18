import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import re
from spotipy.cache_handler import CacheFileHandler

class SpotifyClient:
    def __init__(self):
        print("[DEBUG] Initializing SpotifyClient...")
        client_id = os.getenv('SPOTIFY_CLIENT_ID')
        client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

        if not client_id or not client_secret:
            raise ValueError("Spotify credentials not found in environment variables")

        try:
            # Create cache directory if it doesn't exist
            cache_dir = os.path.join(os.getcwd(), '.spotify_cache')
            os.makedirs(cache_dir, exist_ok=True)
            os.chmod(cache_dir, 0o777)

            cache_path = os.path.join(cache_dir, 'spotify_token.cache')
            print(f"[DEBUG] Using cache path: {cache_path}")

            cache_handler = CacheFileHandler(cache_path=cache_path)

            auth_manager = SpotifyClientCredentials(
                client_id=client_id,
                client_secret=client_secret,
                cache_handler=cache_handler
            )
            print("[DEBUG] Created SpotifyClientCredentials with cache handler")

            self.sp = spotipy.Spotify(auth_manager=auth_manager)
            print("[DEBUG] Successfully initialized Spotify client")

        except Exception as e:
            print(f"[ERROR] Failed to initialize Spotify client: {str(e)}")
            raise

    def extract_spotify_id(self, url):
        """Extract Spotify ID from URL"""
        pattern = r'(?:spotify\.com|open\.spotify\.com)/(?:track|playlist|album)/([a-zA-Z0-9-_]+)'
        match = re.search(pattern, url)
        return match.group(1) if match else None

    def get_content_type(self, url):
        """Determine if URL is for track, playlist, or album"""
        if 'track' in url:
            return 'track'
        elif 'playlist' in url:
            return 'playlist'
        elif 'album' in url:
            return 'album'
        return None

    async def get_track_info(self, url):
        """Get track information from Spotify URL"""
        try:
            print(f"[DEBUG] Getting track info for URL: {url}")
            track_id = self.extract_spotify_id(url)
            if not track_id:
                raise ValueError("Invalid Spotify URL")

            print(f"[DEBUG] Extracted track ID: {track_id}")
            track = self.sp.track(track_id)
            print(f"[DEBUG] Successfully retrieved track data from Spotify API")

            return self._format_track_info(track)

        except Exception as e:
            print(f"[ERROR] Failed to get Spotify track info: {str(e)}")
            raise Exception(f"Failed to process Spotify track: {str(e)}")

    async def get_playlist_tracks(self, url):
        """Get all tracks from a Spotify playlist"""
        try:
            print(f"[DEBUG] Getting playlist tracks for URL: {url}")
            playlist_id = self.extract_spotify_id(url)
            if not playlist_id:
                raise ValueError("Invalid Spotify playlist URL")

            print(f"[DEBUG] Extracted playlist ID: {playlist_id}")
            results = self.sp.playlist_tracks(playlist_id)
            tracks = []

            while results:
                for item in results['items']:
                    if item['track']:
                        tracks.append(self._format_track_info(item['track']))

                if results['next']:
                    results = self.sp.next(results)
                else:
                    results = None

            print(f"[DEBUG] Retrieved {len(tracks)} tracks from playlist")
            return tracks

        except Exception as e:
            print(f"[ERROR] Failed to get Spotify playlist tracks: {str(e)}")
            raise Exception(f"Failed to process Spotify playlist: {str(e)}")

    def _format_track_info(self, track):
        """Format track information consistently"""
        artists = [artist['name'] for artist in track['artists']]
        artist_names = ', '.join(artists)
        track_name = track['name']

        return {
            'title': f"{track_name} - {artist_names}",
            'search_query': f"{artist_names} - {track_name} official audio",
            'duration_ms': track['duration_ms'],
            'preview_url': track.get('preview_url'),
            'artists': artists
        }

## Made by dsod
## Discord: dsodd