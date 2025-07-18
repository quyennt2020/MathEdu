import spacy

nlp = spacy.load("en_core_web_sm")

def generate_flashcards_from_transcript(transcript):
    """
    Generates flashcards from a transcript using NLP.

    Args:
        transcript: A list of transcript segments, each with a 'text' key.

    Returns:
        A list of generated flashcards, each with a 'question' and 'answer'.
    """
    full_text = " ".join([line['text'] for line in transcript])
    doc = nlp(full_text)

    flashcards = []
    for chunk in doc.noun_chunks:
        question = f"What is {chunk.text}?"
        answer = chunk.root.head.text
        flashcards.append({'question': question, 'answer': answer})

    return flashcards

if __name__ == '__main__':
    # Example usage:
    from download_transcript import download_transcript

    video_id = "dQw4w9WgXcQ"
    transcript = download_transcript(video_id)
    if transcript:
        flashcards = generate_flashcards_from_transcript(transcript)
        for card in flashcards:
            print(f"Q: {card['question']}")
            print(f"A: {card['answer']}")
            print("-" * 20)
