from video_summarizer import Summarizer
from youtube import VideoExtractor, is_youtube_link


def summarize_video(url):
    if not is_youtube_link(url):
        return "Invalid YouTube URL"

    try:
        extractor = VideoExtractor()
        summarizer = Summarizer()

        # Download metadata
        video_info = extractor.extract_video_info(url)
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
        print(f'Video id: {video_id}, duration: {duration} = {duration // 60}:{duration % 60:02}')
        if duration >= 7200:
            return "Too long video"

        # Get captions
        caption_track = extractor.get_captions_by_priority(subtitles, automatic_captions)
        if not caption_track:
            return f'Captions are not available for video {video_id}'
        ext = caption_track['ext']

        print(f'Using captions track: {caption_track["name"]} ({ext})')

        # Download captions
        downloaded_content = extractor.download_captions(video_id, caption_track)

        # Parse captions
        caption_text = extractor.parse_captions(ext, downloaded_content)

        print(f'Caption length: {len(caption_text)}')

        # Generate summaries
        summaries = summarizer.summarize(caption_text, video_title, video_description)

        if not summaries:
            return "Failed to summarize"

        # Get the thumbnail with the highest preference
        thumbnail_url = None
        if thumbnails:
            best_thumbnail = max(thumbnails, key=lambda x: x.get('preference', 0))
            thumbnail_url = best_thumbnail.get('url')

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

if __name__ == '__main__':
    result = summarize_video('https://www.youtube.com/watch?v=7b9hfk0Da68')
    print(result)
