import json
import os

CACHE_DIR = './cache'


def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
    if not os.path.isdir(CACHE_DIR):
        raise ValueError(f'{CACHE_DIR} is not a directory')


def reuse_cache(video_id, extension):
    cache_file = os.path.join(CACHE_DIR, f'{video_id}.{extension}')

    if os.path.isfile(cache_file):
        print(f'Reusing cached file: {cache_file}')

        if extension == "json":
            return json.load(open(cache_file))
        return open(cache_file).read()
    return None


def create_cache_json(video_id, content):
    cache_file = os.path.join(CACHE_DIR, f'{video_id}.json')
    with open(cache_file, 'w') as f:
        json.dump(content, f, indent=4)


def create_cache(video_id, extension, content):
    cache_file = os.path.join(CACHE_DIR, f'{video_id}.{extension}')
    with open(cache_file, 'w') as f:
        f.write(content)
