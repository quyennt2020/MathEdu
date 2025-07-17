from youtube_transcript_api import YouTubeTranscriptApi

def download_transcript(youtube_id):
    """
    Downloads the transcript for a given YouTube video ID.

    Args:
        youtube_id: The ID of the YouTube video.

    Returns:
        A list of dictionaries, where each dictionary represents a segment of the transcript.
        Each dictionary includes the text, start time, and duration.
        Returns None if the transcript could not be downloaded.
    """
    try:
        transcript = YouTubeTranscriptApi.get_transcript(youtube_id, languages=['en'])
        return transcript
    except Exception as e:
        print(f"Error downloading transcript: {e}")
        return None

if __name__ == '__main__':
    # Example usage:
    video_id = "dQw4w9WgXcQ"  # Rick Astley - Never Gonna Give You Up
    transcript = download_transcript(video_id)
    if transcript:
        for line in transcript:
            print(f"[{line['start']:.2f}s - {line['start'] + line['duration']:.2f}s] {line['text']}")
