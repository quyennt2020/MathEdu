from google.cloud import translate_v2 as translate

def translate_text(text, target_language='vi'):
    """
    Translates text to the target language using Google Cloud Translate.

    Args:
        text: The text to translate.
        target_language: The target language code (e.g., 'vi' for Vietnamese).

    Returns:
        The translated text.
    """
    translate_client = translate.Client()
    result = translate_client.translate(text, target_language=target_language)
    return result['translatedText']

if __name__ == '__main__':
    # Example usage:
    from download_transcript import download_transcript

    video_id = "dQw4w9WgXcQ"
    transcript = download_transcript(video_id)
    if transcript:
        for line in transcript:
            english_text = line['text']
            vietnamese_text = translate_text(english_text)
            print(f"English: {english_text}")
            print(f"Vietnamese: {vietnamese_text}")
            print("-" * 20)
