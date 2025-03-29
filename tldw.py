import sys
from youtube import YoutubeVideoInfoExtractor
from youtube_captions import YoutubeVideoCaptionsExtractor
from youtube_summarizer import YoutubeSummarizer

url = sys.argv[1]

def summarize_video(url):
    try:
        # Download metadata
        youtube_video_info_extractor = YoutubeVideoInfoExtractor()
        video_info = youtube_video_info_extractor.extract_video_info(url)
        if not video_info:
            return "Failed to download video info"

        video_id = video_info.get('id')
        duration = video_info.get('duration')
        video_title = video_info.get("fulltitle")
        video_description = video_info.get("description")
        aspect_ratio = video_info.get('aspect_ratio', 1.78)
        webpage_url = video_info.get('webpage_url', 'https://www.youtube.com/watch?v=' + video_id)
        thumbnails = video_info.get('thumbnails', [])
        title = video_info.get('title', '')
        subtitles = video_info.get('subtitles')
        automatic_captions = video_info.get('automatic_captions')

        # If video too long, reject
        if duration >= 7200:
            return "Too long video"

        # Get captions
        youtube_video_captions_extractor = YoutubeVideoCaptionsExtractor()
        caption_text = youtube_video_captions_extractor.prepare_captions(video_id, subtitles, automatic_captions)
        if not caption_text:
            return f'Captions are not available for video {video_id}'

        # Generate summaries
        youtube_summarizer = YoutubeSummarizer()
        summaries = youtube_summarizer.summarize(video_id, caption_text, video_title, video_description)
        if not summaries:
            return "Failed to summarize"

        thumbnail_url = prepare_thumbnail_url(thumbnails)

        return {
            "success": True,
            "error": "",
            "video_id": video_id,
            "title": title,
            "thumbnail_url": thumbnail_url,
            "aspect_ratio": aspect_ratio,
            "webpage_url": webpage_url,
            "summary": summaries
        }

    except Exception as e:
        return f"An error occurred: {str(e)}"


def prepare_thumbnail_url(thumbnails):
    if thumbnails:
        best_thumbnail = max(thumbnails, key=lambda x: x.get('preference', 0))
        return best_thumbnail.get('url')
    return None


summarize = summarize_video(url)

print(summarize)
