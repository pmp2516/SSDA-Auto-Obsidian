def chunk_markdown(text, max_chunk_size=1000):
    """
    Split the markdown input by all headers, hlines and if the max_chars per chunk is reached (mxax_chunk_size).

    Args:
        text (str): The markdown text to be chunked.
        max_chunk_size (int): The maximum number of characters allowed in each chunk.

    Returns:
        list: A list of markdown chunks.
    """

    chunks = []
    current_chunk = ""

    lines = text.splitlines()
    for line in lines:
        # Check if the line is a header or a horizontal line
        if line.startswith("#") or line.startswith("---") or len(current_chunk) + len(line) > max_chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""
        current_chunk += line + "\n"

    # Add any remaining content as a chunk
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks