from lyricsgenius.api import Genius
from config import genius_client_access_token, s3_bucket
import yaml
import json
from tqdm import tqdm
import boto3

genius_api = Genius(genius_client_access_token, verbose=True)
bucket = boto3.resource("s3").Bucket(s3_bucket)
MAX_SONGS = 50

with open("artist_list.yaml", 'r') as f:
    artists_names = yaml.load(f, Loader=yaml.FullLoader)


songs = []
for artist_name in tqdm(artists_names):
    try:
        artist = genius_api.search_artist(artist_name, max_songs=MAX_SONGS)
    except KeyboardInterrupt as e:
        raise e
    except:
        print(f"Could not fetch results for artist : {artist_name}. Continuing...")
        continue

    for song in artist.songs:
        songs.append({
            "artist_name": artist_name,
            "artist_name_genius": artist.name,
            "song": song.title,
            "lyrics": song.lyrics,
            "year": song.year[:4] if song.year is not None else None,
            "featured_artists": song.featured_artists,
            "url": song._url
        })

bucket.Object(key="lyrics_data.json").put(Body=json.dumps(songs, sort_keys=True, indent=4))
