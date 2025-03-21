import json
import os

CACHE_DIR = './cache'


def ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)
    if not os.path.isdir(CACHE_DIR):
        raise ValueError(f'{CACHE_DIR} is not a directory')


def reuse_cache_json(video_id):
    cache_file = os.path.join(CACHE_DIR, f'{video_id}.json')

    if os.path.isfile(cache_file):
        print(f'Reusing cached file: {cache_file}')

        return json.load(open(cache_file))
    return None


def reuse_cache_txt(video_id):
    cache_file = os.path.join(CACHE_DIR, f'{video_id}.txt')

    if os.path.isfile(cache_file):
        print(f'Reusing cached file: {cache_file}')

        with open(cache_file, "r", encoding="utf-8") as f:
            return f.read()
    return None


def create_cache_json(video_id, content):
    cache_file = os.path.join(CACHE_DIR, f'{video_id}.json')
    with open(cache_file, 'w') as f:
        json.dump(content, f, indent=4)


def create_cache_txt(video_id, content):
    cache_file = os.path.join(CACHE_DIR, f'{video_id}.txt')
    with open(cache_file, 'w', encoding="utf-8") as f:
        f.write(content)
