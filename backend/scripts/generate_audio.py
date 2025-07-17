from gtts import gTTS
import os

def generate_audio_segments(transcript, language='vi', output_dir='audio_segments'):
    """
    Generates audio files for each line of the transcript.

    Args:
        transcript: A list of transcript segments, each with a 'text' key.
        language: The language of the text.
        output_dir: The directory to save the audio files.

    Returns:
        A list of filenames for the generated audio files.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    filenames = []
    for i, line in enumerate(transcript):
        try:
            tts = gTTS(text=line['text'], lang=language, slow=False)
            filename = os.path.join(output_dir, f"segment_{i}.mp3")
            tts.save(filename)
            filenames.append(filename)
        except Exception as e:
            print(f"Error generating audio for segment {i}: {e}")

    return filenames

if __name__ == '__main__':
    # Example usage:
    from download_transcript import download_transcript
    from translate_transcript import translate_text

    video_id = "dQw4w9WgXcQ"
    transcript = download_transcript(video_id)
    if transcript:
        # Translate the transcript
        for line in transcript:
            line['text'] = translate_text(line['text'])

        generate_audio_segments(transcript)
