import re

def chunk_text(text, chunk_size=500, overlap=50):
    """Split text into chunks while keeping sentence boundaries."""

    sentences = re.split(r'(?<=[.!?])\s+', text.strip())

    chunks = []
    chunk = ""

    for sentence in sentences:

        if len(chunk) + len(sentence) <= chunk_size:
            chunk += sentence + " "
        else:
            if chunk:
                chunks.append(chunk.strip())

            if overlap:
                chunk = chunk[-overlap:]

            chunk += sentence + " "

    if chunk:
        chunks.append(chunk.strip())

    return chunks