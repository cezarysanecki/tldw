from typing import Dict, Optional, Tuple

import yt_dlp
from yt_dlp.utils import YoutubeDLError

from cache import ensure_cache_dir, create_cache_json, reuse_cache_json


class YoutubeVideoInfoExtractor:
    def __init__(self):
        ensure_cache_dir()

        self.ydl_opts = {
            'writesubtitles': True,
            'writeannotations': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['en', 'en-US', 'en-CA'],  # Focus on English captions for now
            'skip_download': True,  # Don't download the video file
            'quiet': False,
            'no_warnings': False,
            'no-playlist': True
        }

    def extract_video_info(self, url: str) -> Tuple[Optional[Dict], Optional[str]]:
        """
        Extract video description and captions from a YouTube URL.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Tuple containing:
            - Dictionary with video information (title, description)
            - String containing the captions/subtitles
        """

        print("=== GATHERING VIDEO INFO ===")
        try:
            video_id = yt_dlp.extractor.youtube.YoutubeIE.extract_id(url)
        except YoutubeDLError as e:
            print(f"Failed to download video info for {url}: {str(e)}")
            raise Exception(f"Cannot extract id for {url}")

        result = reuse_cache_json(video_id)
        if result:
            return result

        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Get video info
                video_info = ydl.extract_info(url, download=False)
        except YoutubeDLError as e:
            print(f"Error extracting video information: {str(e)}")
            raise Exception(f"Cannot extract info for {url}")

        duration = video_info.get('duration')
        print(f'Video id: {video_id}, duration: {duration} = {duration // 60}:{duration % 60:02}')

        create_cache_json(video_id, video_info)

        return video_info
