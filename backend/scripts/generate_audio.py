from gtts import gTTS
import os

def generate_audio(text, language='vi', filename='output.mp3'):
    """
    Generates an audio file from text using Google Text-to-Speech.

    Args:
        text: The text to convert to speech.
        language: The language of the text (e.g., 'vi' for Vietnamese).
        filename: The name of the output audio file.
    """
    try:
        tts = gTTS(text=text, lang=language, slow=False)
        tts.save(filename)
        print(f"Audio content written to file '{filename}'")
    except Exception as e:
        print(f"Error generating audio: {e}")

if __name__ == '__main__':
    # Example usage:
    from translate_transcript import translate_text
    from download_transcript import download_transcript

    video_id = "dQw4w9WgXcQ"
    transcript = download_transcript(video_id)
    if transcript:
        full_transcript_text = " ".join([line['text'] for line in transcript])
        vietnamese_text = translate_text(full_transcript_text)
        generate_audio(vietnamese_text)
