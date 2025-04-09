import re
from typing import Dict, Optional

import requests
import webvtt

from utils.cache import reuse_cache_txt, ensure_cache_dir, create_cache_txt
from utils.time_utils import ts_to_secs, seconds_to_timestamp, timestamp_to_seconds


class YoutubeVideoCaptionsExtractor:
    def __init__(self):
        ensure_cache_dir()

    def prepare_captions(self, video_id, subtitles, automatic_captions):
        print("=== PREPARING VIDEO CAPTIONS ===")

        result = reuse_cache_txt(video_id)
        if result:
            return result

        # Get captions
        caption_track = self.__get_captions_by_priority(subtitles, automatic_captions)
        if not caption_track:
            print(f'Captions are not available for video {video_id}')
            return None

        ext = caption_track['ext']
        name = caption_track["name"]
        url = caption_track['url']

        print(f'Using captions track: {name} ({ext})')
        downloaded_content = self.__download_captions(url)
        caption_text = self.__parse_captions(ext, downloaded_content)

        print(f'Caption length: {len(caption_text)}')

        create_cache_txt(video_id, caption_text)

        return caption_text

    def __get_captions_by_priority(self, subtitles, automatic_captions) -> Optional[Dict]:
        """
        Get captions based on priority order:
        1. Manual subtitles (en-US, en-CA, en-*)
        2. Automatic captions (en-orig, en-US, en-CA, en)

        Args:
            subtitles: Video subtitles from yt-dlp
            automatic_captions: Video automatic captions from yt-dlp

        Returns:
            Caption json blob (fields ext, url, name)
        """
        # Priority order for subtitle languages
        subtitle_priorities = ['en-US', 'en-CA', 'en']
        auto_caption_priorities = ['en-orig', 'en-US', 'en-CA', 'en']
        format_priorities = ['vtt', 'srt', 'ttml']

        caption_track = None

        # Check manual subtitles first
        if subtitles:
            # Check specific language variants first
            for lang in subtitle_priorities:
                if lang in subtitles:
                    caption_track = subtitles[lang]
                    break

            # Then check for any other en-* variants
            else:
                for lang in subtitles.keys():
                    if lang.startswith('en-'):
                        caption_track = subtitles[lang]
                        break

        # Check automatic captions if no manual subtitles found
        if not caption_track:
            if automatic_captions:
                for lang in auto_caption_priorities:
                    if lang in automatic_captions:
                        caption_track = automatic_captions[lang]
                        break

        if not caption_track:
            return None

        # Find the preferred format
        for format in format_priorities:
            for track in caption_track:
                if not 'name' in track or track.get('protocol') == 'm3u8_native':  # skip weird m3u8 captions
                    continue
                if track.get('ext') == format:
                    return track

        # If no compatible format found, fail
        return None

    def __download_captions(self, url: str) -> str:
        # Download caption content
        response = requests.get(url)
        response.raise_for_status()
        content = response.text

        return content

    def __parse_captions(self, ext: str, content: str) -> str:
        """
        Parse caption content with formatting based on timing.

        Args:
            ext: Captions file extension
            content: Downloaded captions content

        Returns:
            Plain text of the captions with paragraph breaks for pauses > 3 seconds

        Raises:
            ValueError: If caption format is not supported
        """

        if ext == 'vtt':
            captions = webvtt.from_string(content)
            result = ''

            captions = list(self.__dedupe_yt_captions(captions))

            for i, caption in enumerate(captions):
                # Clean up the current caption text
                current_text = caption.text.replace('\n', ' ').strip()

                if i > 0:
                    # Calculate time difference with previous caption
                    prev_end = timestamp_to_seconds(captions[i - 1].end)
                    current_start = timestamp_to_seconds(caption.start)
                    time_diff = current_start - prev_end

                    # Add double newline for pauses > 3 seconds, space otherwise
                    if time_diff >= 2:
                        result += '\n\n'
                    elif time_diff >= 1:
                        result += '\n'
                    else:
                        result += ' '

                result += current_text
        else:
            raise ValueError(f"Unsupported caption format: {ext}")

        # Final cleanup to remove any multiple spaces
        result = ' '.join(re.split(' +', result))

        return result

    # adapted from https://github.com/bindestriche/srt_fix/blob/5b4442a8cdcae06c53545f4d0c99c3e624416919/simplesrt.py#L132C1-L201C28
    def __dedupe_yt_captions(self, subs_iter):
        previous_subtitle = None
        for subtitle in subs_iter:

            if previous_subtitle is None:  # first interation set previous subtitle for comparison
                previous_subtitle = subtitle
                continue

            subtitle.text = subtitle.text.strip()  # remove trailing linebreaks

            if len(subtitle.text) == 0:  # skip over empty subtitles
                continue

            if (ts_to_secs(subtitle.start_time) - ts_to_secs(subtitle.end_time) < 0.15 and  # very short
                    subtitle.text in previous_subtitle.text):  # same text as previous
                previous_subtitle.end = subtitle.end  # lengthen previous subtitle
                continue

            current_lines = subtitle.text.split("\n")
            last_lines = previous_subtitle.text.split("\n")

            singleword = False

            if current_lines[0] == last_lines[-1]:  # if first current is  last previous
                if len(last_lines) == 1:
                    if len(last_lines[0].split(" ")) < 2 and len(last_lines[0]) > 2:  # if  is just one word
                        singleword = True
                        subtitle.text = current_lines[0] + " " + "\n".join(
                            current_lines[1:])  # remove line break after single word

                    else:
                        subtitle.text = "\n".join(current_lines[1:])  # discard first line of current
                else:
                    subtitle.text = "\n".join(current_lines[1:])  # discard first line of current
            else:  # not fusing two lines
                if len(subtitle.text.split(" ")) <= 2:  # only one word in subtitle

                    previous_subtitle.end = subtitle.end  # lengthen previous subtitle
                    title_text = subtitle.text
                    if title_text[0] != " ":
                        title_text = " " + title_text

                    previous_subtitle.text += title_text  # add text to previous
                    continue  # drop this subtitle

            if ts_to_secs(subtitle.start_time) <= ts_to_secs(
                    previous_subtitle.end_time):  # remove overlap and let 1ms gap
                new_time = max(ts_to_secs(subtitle.start_time) - 0.001, 0)
                previous_subtitle.end = seconds_to_timestamp(new_time)
            if ts_to_secs(subtitle.start_time) >= ts_to_secs(
                    subtitle.end_time):  # swap start and end if wrong order
                subtitle.start, subtitle.end = subtitle.end, subtitle.start

            if not singleword:
                yield previous_subtitle
            previous_subtitle = subtitle
        yield previous_subtitle
