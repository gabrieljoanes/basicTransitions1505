# utils/logger.py

import os
from datetime import datetime

def save_output_to_file(title: str, chapo: str, article_text: str, transitions: list[str]):
    """
    Saves the generated article and transitions to a timestamped text file.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"generated_output_{timestamp}.txt"
    output_dir = "outputs"

    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"Titre: {title}\n\n")
        f.write(f"Chapeau: {chapo}\n\n")
        f.write("Article:\n")
        f.write(article_text.strip() + "\n\n")
        f.write("Transitions générées:\n")
        for i, t in enumerate(transitions, 1):
            f.write(f"{i}. {t}\n")

    return filepath
