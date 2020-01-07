import boto3
import json
import time


class S3Manager:

    def __init__(self, bucket_name):
        self.bucket_name = bucket_name
        self.bucket = boto3.resource('s3').Bucket(self.bucket_name)
        self.client = boto3.client("s3")

    def list_keys(self, prefix=None, suffix=None):
        if prefix is None:
            prefix = ''
        response = self.client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix
        )

        if 'Contents' not in response:
            return []

        keys = list(map(lambda obj: obj["Key"], response['Contents']))

        if suffix is not None:
            keys = [key for key in keys if key.endswith(suffix)]

        return keys

    def get_latest_song_data(self):
        songs_jsons = self.list_keys(prefix="songs-data", suffix=".json")
        if not len(songs_jsons):
            return None

        last_song_json = max(songs_jsons)

        obj = (
            self.client.get_object(Bucket=self.bucket_name, Key=last_song_json)
            ["Body"].read().decode("utf-8")
        )

        return json.loads(obj)

    def save_song_data(self, songs):
        return (
            self.bucket.Object(key=f"songs-data-{time.strftime('%Y%m%d-%H%M')}.json")
            .put(Body=json.dumps(songs, sort_keys=True, indent=4))
        )


if __name__ == "__main__":
    s3_manager = S3Manager("rap-embedding")
    print(s3_manager.list_keys(suffix='.json'))
    print(s3_manager.get_latest_song_data()[:3])
