def load_text_file(text_file: str) -> str:
    with open(text_file, 'r') as f:
        return f.read()
